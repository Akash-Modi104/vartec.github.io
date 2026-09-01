import { Component, OnInit } from '@angular/core';
import { CmsApiService } from '../cms-api.service';
import { DashboardResponse, ResourceMeta } from '../models';

@Component({ selector: 'cms-dashboard', templateUrl: './dashboard.component.html' })
export class DashboardComponent implements OnInit {
  data?: DashboardResponse;
  loading = true;
  error = '';
  readonly quickKeys = ['pages', 'text', 'media', 'enquiries'];

  constructor(private api: CmsApiService) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true;
    this.api.dashboard().subscribe({
      next: data => { this.data = data; this.loading = false; },
      error: error => { this.error = error.error?.detail || 'Dashboard information could not be loaded.'; this.loading = false; }
    });
  }
  resource(key: string): ResourceMeta | undefined { return this.data?.resources.find(item => item.key === key); }
  groups(): string[] { return Array.from(new Set((this.data?.resources || []).map(item => item.group))); }
  inGroup(group: string): ResourceMeta[] { return (this.data?.resources || []).filter(item => item.group === group); }
}
