import { Component, OnDestroy, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { CmsApiService } from '../cms-api.service';
import { CmsField, CmsItem, DetailResponse, ResourceMeta, ResourceResponse } from '../models';

@Component({ selector: 'cms-editor', templateUrl: './editor.component.html' })
export class EditorComponent implements OnInit, OnDestroy {
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
  filters: Record<string, string> = {};
  success = '';
  private subscription = new Subscription();

  constructor(private fb: FormBuilder, private route: ActivatedRoute, private router: Router, private api: CmsApiService) {}
  ngOnInit(): void {
    this.subscription.add(this.route.paramMap.subscribe(params => {
      this.resourceKey = params.get('resource') || '';
      const id = params.get('id'); this.objectId = id ? Number(id) : undefined;
      this.loading = true; this.error = ''; this.files = {}; this.fieldErrors = {};
      if (this.selectedPreview) URL.revokeObjectURL(this.selectedPreview);
      this.selectedPreview = ''; this.selectedPreviewType = '';
      this.filters = {};
      this.success = this.route.snapshot.queryParamMap.get('created') ? 'Created successfully. You can now add content below.' : '';
      for (const name of ['kind', 'page', 'section', 'block']) { const value = this.route.snapshot.queryParamMap.get(name); if (value) this.filters[name] = value; }
      const request: Observable<DetailResponse | ResourceResponse> = this.objectId ? this.api.detail(this.resourceKey, this.objectId) : this.api.list(this.resourceKey);
      this.subscription.add(request.subscribe({next: response => this.setup(response.resource, response.schema, 'item' in response ? response.item : undefined), error: error => this.fail(error)}));
    }));
  }
  ngOnDestroy(): void { this.subscription.unsubscribe(); if (this.selectedPreview) URL.revokeObjectURL(this.selectedPreview); }
  setup(meta: ResourceMeta, fields: CmsField[], item?: CmsItem): void {
    this.meta = meta; this.fields = fields; this.item = item;
    const controls: Record<string, FormControl> = {};
    for (const field of fields) {
      let value = item?.fields[field.name] ?? this.filters[field.name] ?? field.default ?? (field.type === 'boolean' ? false : '');
      if (field.type === 'file') value = '';
      if (field.type === 'datetime' && typeof value === 'string') value = value.slice(0, 16);
      const required = field.required || (!item && this.resourceKey === 'sections' && field.name === 'title_key_text');
      controls[field.name] = new FormControl({ value, disabled: field.readonly }, required && field.type !== 'file' ? Validators.required : []);
    }
    this.form = this.fb.group(controls);
    this.loading = false;
    const group = this.route.snapshot.queryParamMap.get('group');
    if (group) window.setTimeout(() => this.jumpTo(this.groups().indexOf(group)), 0);
  }
  fail(error: any): void { this.error = error.error?.detail || 'This item could not be loaded.'; this.loading = false; }
  control(field: CmsField): AbstractControl | null { return this.form.get(field.name); }
  nonBooleanFields(): CmsField[] { return this.fields.filter(field => field.type !== 'boolean'); }
  booleanFields(): CmsField[] { return this.fields.filter(field => field.type === 'boolean'); }
  groupFor(field: CmsField): string {
    const name = field.name;
    if (name.startsWith('legacy_') || ['key', 'published_at', 'slug', 'admin_name', 'kind'].includes(name) && this.resourceKey !== 'media') return 'Advanced';
    if (this.resourceKey === 'settings') {
      if (name.startsWith('chatbot_')) return 'Website assistant';
      if (['contact_email', 'uk_phone', 'notification_email'].includes(name)) return 'Contact details';
      if (name.startsWith('default_seo_') || name === 'organisation_schema_enabled') return 'Search engines';
      if (name.endsWith('_enabled') || name === 'video') return 'Homepage sections';
      return 'Brand & appearance';
    }
    if (name.startsWith('seo_')) return 'Search engines';
    if (field.type === 'boolean' || name === 'sort_order') return 'Visibility & order';
    if (field.type === 'file' || ['media', 'card_media', 'alt_text_key_text'].includes(name)) return 'Images & video';
    if (['layout', 'background'].includes(name)) return 'Layout & theme';
    return 'Content';
  }
  visibleFields(): CmsField[] { return this.fields.filter(field => !this.filters[field.name] || !['kind', 'page', 'section', 'block'].includes(field.name)); }
  groups(): string[] {
    const order = ['Content', 'Images & video', 'Layout & theme', 'Visibility & order', 'Brand & appearance', 'Contact details', 'Homepage sections', 'Website assistant', 'Search engines', 'Advanced'];
    return Array.from(new Set(this.visibleFields().map(field => this.groupFor(field)))).sort((a,b) => order.indexOf(a) - order.indexOf(b));
  }
  jumpTo(index: number, event?: Event): void {
    event?.preventDefault(); if (index < 0) return;
    const target = document.getElementById('group-' + index);
    if (target instanceof HTMLDetailsElement) target.open = true;
    target?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'start'});
  }
  groupFields(group: string): CmsField[] { return this.visibleFields().filter(field => this.groupFor(field) === group); }
  fieldLabel(field: CmsField): string {
    if (field.name === 'title_key_text' && this.resourceKey === 'pages') return this.form.get('kind')?.value === 'project' ? 'Project name' : 'Service name';
    if (field.name === 'title_key_text' && this.resourceKey === 'sections') return 'Section heading';
    return field.label;
  }
  parentLabel(): string {
    const name = ['page', 'section', 'block'].find(value => this.filters[value]);
    return name ? this.fields.find(field => field.name === name)?.options?.find(option => String(option.value) === this.filters[name])?.label || '' : '';
  }
  parentRoute(): string[] {
    const name = ['page', 'section', 'block'].find(value => this.filters[value]);
    const resources: Record<string,string> = {page:'pages',section:'sections',block:'home-blocks'};
    return name ? ['/content',resources[name],this.filters[name]] : ['/content',this.resourceKey];
  }
  description(group: string): string {
    return ({'Content':'Edit the wording here, just as it appears on the website.', 'Images & video':'Choose an existing library item or upload a file.', 'Visibility & order':'Choose where this appears. Lower display numbers appear first.', 'Layout & theme':'Choose the arrangement and background for this section.', 'Search engines':'Optional titles and descriptions for search results.', 'Brand & appearance':'Logo, colours and typography used across the site.', 'Contact details':'Public contact information and enquiry notifications.', 'Homepage sections':'Show or hide each homepage section and choose the About Us video.', 'Website assistant':'Set the welcome message and show or hide the help chat.', 'Advanced':'Internal identifiers and older file paths. Usually no changes are needed.'} as Record<string,string>)[group] || '';
  }
  children(): {resource:string; parent:string; label:string} | undefined {
    return ({pages:{resource:'sections',parent:'page',label:'Page sections'}, sections:{resource:'section-items',parent:'section',label:'Paragraphs & lists'}, 'home-blocks':{resource:'home-features',parent:'block',label:'Feature cards'}} as Record<string, {resource:string;parent:string;label:string}>)[this.resourceKey];
  }
  childParams(): Record<string, string | number> { const child = this.children(); return child && this.objectId ? {[child.parent]:this.objectId} : {}; }
  openChildren(): void {
    const child = this.children(); if (!child || !this.objectId) return;
    if ((this.form.dirty || Object.keys(this.files).length) && !window.confirm('Discard your unsaved changes and open the related content?')) return;
    this.router.navigate(['/content', child.resource], {queryParams:this.childParams()});
  }
  addChild(): void {
    const child = this.children(); if (!child || !this.objectId) return;
    if ((this.form.dirty || Object.keys(this.files).length) && !window.confirm('Discard your unsaved changes and add related content?')) return;
    this.router.navigate(['/content',child.resource,'new'], {queryParams:this.childParams()});
  }
  backLabel(): string { return this.filters['kind'] === 'service' ? 'Services' : this.filters['kind'] === 'project' ? 'Projects' : this.meta?.plural || 'Back'; }
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
    this.router.navigate(['/content', this.resourceKey], {queryParams:this.filters});
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
      next: response => {
        this.saving = false; this.form.markAsPristine(); this.files = {};
        if (!this.objectId && this.children()) this.router.navigate(['/content',this.resourceKey,response.item.id], {queryParams:{...this.filters,created:'1'}});
        else this.router.navigate(['/content', this.resourceKey], {queryParams:this.filters});
      },
      error: error => {
        this.error = error.error?.detail || 'The changes could not be saved.'; this.fieldErrors = error.error?.errors || {}; this.saving = false;
        const advanced = document.querySelector('details.advanced-card');
        if (advanced instanceof HTMLDetailsElement && this.groupFields('Advanced').some(field => this.fieldErrors[field.name])) advanced.open = true;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }
}
