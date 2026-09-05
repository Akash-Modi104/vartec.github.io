import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { CmsApiService } from '../cms-api.service';
import { CmsField, CmsItem, ResourceMeta } from '../models';

@Component({ selector: 'cms-editor', templateUrl: './editor.component.html' })
export class EditorComponent implements OnInit {
  resourceKey = '';
  objectId?: number;
  meta?: ResourceMeta;
  item?: CmsItem;
  fields: CmsField[] = [];
  form: FormGroup = this.fb.group({});
  files: Record<string, File> = {};
  loading = true;
  saving = false;
  error = '';
  fieldErrors: Record<string, string[]> = {};
  selectedPreview = '';
  selectedPreviewType = '';

  constructor(private fb: FormBuilder, private route: ActivatedRoute, private router: Router, private api: CmsApiService) {}
  ngOnInit(): void {
    this.resourceKey = this.route.snapshot.paramMap.get('resource') || '';
    const id = this.route.snapshot.paramMap.get('id');
    this.objectId = id ? Number(id) : undefined;
    if (this.objectId) {
      this.api.detail(this.resourceKey, this.objectId).subscribe({ next: response => this.setup(response.resource, response.schema, response.item), error: error => this.fail(error) });
    } else {
      this.api.list(this.resourceKey, '', 1).subscribe({ next: response => this.setup(response.resource, response.schema), error: error => this.fail(error) });
    }
  }
  setup(meta: ResourceMeta, fields: CmsField[], item?: CmsItem): void {
    this.meta = meta; this.fields = fields; this.item = item;
    const controls: Record<string, FormControl> = {};
    for (const field of fields) {
      let value = item?.fields[field.name] ?? field.default ?? (field.type === 'boolean' ? false : '');
      if (field.type === 'file') value = '';
      if (field.type === 'datetime' && typeof value === 'string') value = value.slice(0, 16);
      controls[field.name] = new FormControl({ value, disabled: field.readonly }, field.required && field.type !== 'file' ? Validators.required : []);
    }
    this.form = this.fb.group(controls);
    this.loading = false;
  }
  fail(error: any): void { this.error = error.error?.detail || 'This item could not be loaded.'; this.loading = false; }
  control(field: CmsField): AbstractControl | null { return this.form.get(field.name); }
  nonBooleanFields(): CmsField[] { return this.fields.filter(field => field.type !== 'boolean'); }
  booleanFields(): CmsField[] { return this.fields.filter(field => field.type === 'boolean'); }
  currentFile(field: CmsField): { name: string; url: string } | null {
    const value = this.item?.fields[field.name];
    return value && typeof value === 'object' ? value : null;
  }
  pickFile(field: CmsField, event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      const file = input.files[0];
      this.files[field.name] = file;
      if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
        if (this.selectedPreview) URL.revokeObjectURL(this.selectedPreview);
        this.selectedPreview = URL.createObjectURL(file);
        this.selectedPreviewType = file.type.startsWith('video/') ? 'video' : 'image';
      }
    }
  }
  previewUrl(): string { return this.selectedPreview || this.item?.preview || ''; }
  previewType(): string { return this.selectedPreviewType || this.item?.previewType || ''; }
  cancel(): void {
    if ((this.form.dirty || Object.keys(this.files).length) && !window.confirm('Discard your unsaved changes?')) return;
    this.router.navigate(['/content', this.resourceKey]);
  }
  save(): void {
    if (this.form.invalid || this.saving) { this.form.markAllAsTouched(); return; }
    this.saving = true; this.error = ''; this.fieldErrors = {};
    const payload = new FormData();
    for (const field of this.fields) {
      if (field.readonly) continue;
      if (field.type === 'file') {
        if (this.files[field.name]) payload.append(field.name, this.files[field.name]);
        continue;
      }
      const value = this.form.get(field.name)?.value;
      payload.append(field.name, value === null || value === undefined ? '' : String(value));
    }
    const request = this.objectId ? this.api.update(this.resourceKey, this.objectId, payload) : this.api.create(this.resourceKey, payload);
    request.subscribe({
      next: () => this.router.navigate(['/content', this.resourceKey]),
      error: error => { this.error = error.error?.detail || 'The changes could not be saved.'; this.fieldErrors = error.error?.errors || {}; this.saving = false; window.scrollTo({ top: 0, behavior: 'smooth' }); }
    });
  }
}
