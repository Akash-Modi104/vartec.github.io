import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { CmsApiService } from '../cms-api.service';
import { CmsItem, ListField, Pagination, ResourceMeta } from '../models';

@Component({ selector: 'cms-resource-list', templateUrl: './resource-list.component.html' })
export class ResourceListComponent implements OnInit, OnDestroy {
  resourceKey = '';
  meta?: ResourceMeta;
  items: CmsItem[] = [];
  fields: ListField[] = [];
  pagination?: Pagination;
  query = '';
  loading = true;
  error = '';
  private search$ = new Subject<string>();
  private subscriptions = new Subscription();

  constructor(private route: ActivatedRoute, private router: Router, private api: CmsApiService) {}
  ngOnInit(): void {
    this.subscriptions.add(this.route.paramMap.subscribe(params => { this.resourceKey = params.get('resource') || ''; this.query = ''; this.load(1); }));
    this.subscriptions.add(this.search$.pipe(debounceTime(300), distinctUntilChanged()).subscribe(() => this.load(1)));
  }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  search(value: string): void { this.query = value; this.search$.next(value); }
  load(page = 1): void {
    this.loading = true; this.error = '';
    this.api.list(this.resourceKey, this.query, page).subscribe({
      next: response => { this.meta = response.resource; this.items = response.items; this.fields = response.listFields; this.pagination = response.pagination; this.loading = false; },
      error: error => { this.error = error.error?.detail || 'This content could not be loaded.'; this.loading = false; }
    });
  }
  create(): void { this.router.navigate(['/content', this.resourceKey, 'new']); }
  edit(item: CmsItem): void { this.router.navigate(['/content', this.resourceKey, item.id]); }
  toggle(item: CmsItem, event: Event): void {
    event.stopPropagation();
    const value = !Boolean(item.fields['is_active']);
    item.fields['is_active'] = value;
    item.cells['is_active'] = value ? 'Yes' : 'No';
    this.api.update(this.resourceKey, item.id, { is_active: value }).subscribe({ error: () => { item.fields['is_active'] = !value; item.cells['is_active'] = !value ? 'Yes' : 'No'; } });
  }
  remove(item: CmsItem, event: Event): void {
    event.stopPropagation();
    if (!window.confirm(`Delete “${item.display}”? This cannot be undone.`)) return;
    this.api.delete(this.resourceKey, item.id).subscribe({ next: () => this.load(this.pagination?.page || 1), error: error => this.error = error.error?.detail || 'This item could not be deleted.' });
  }
  isStatus(field: ListField): boolean { return ['status', 'kind', 'background', 'item_type'].includes(field.name); }
  isActive(field: ListField): boolean { return field.name === 'is_active'; }
  hasActive(): boolean { return this.fields.some(field => field.name === 'is_active'); }
  hasPreviews(): boolean { return this.items.some(item => Boolean(item.preview)); }
  page(direction: number): void { if (this.pagination) this.load(this.pagination.page + direction); }
}
