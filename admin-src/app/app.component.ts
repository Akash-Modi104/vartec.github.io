import { Component, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import { CmsApiService } from './cms-api.service';

interface NavItem { key: string; label: string; mark: string; kind?: string; }
interface NavGroup { label: string; items: NavItem[]; }

@Component({ selector: 'cms-root', templateUrl: './app.component.html' })
export class AppComponent implements OnInit {
  mobileOpen = false;
  currentUrl = this.router.url;
  readonly user$ = this.api.user$;
  readonly groups: NavGroup[] = [
    { label: 'Website content', items: [{ key: 'home-blocks', label: 'Homepage', mark: '⌂' }, { key: 'pages', label: 'Services', mark: 'S', kind: 'service' }, { key: 'pages', label: 'Projects', mark: 'P', kind: 'project' }, { key: 'text', label: 'Shared website wording', mark: 'T' }] },
    { label: 'Manage', items: [{ key: 'media', label: 'Media library', mark: '▧' }, { key: 'enquiries', label: 'Enquiries', mark: '✉' }, { key: 'settings', label: 'Website settings', mark: '⚙' }] }
  ];

  constructor(public api: CmsApiService, private router: Router) {
    this.router.events.pipe(filter(event => event instanceof NavigationEnd)).subscribe(event => {
      this.currentUrl = (event as NavigationEnd).urlAfterRedirects;
      this.mobileOpen = false;
      window.scrollTo({ top: 0, behavior: 'auto' });
    });
  }

  ngOnInit(): void { this.api.session().subscribe(); }
  isLogin(): boolean { return this.currentUrl.startsWith('/login'); }
  isActive(key: string, kind?: string): boolean {
    if (kind) return this.currentUrl.includes(`/content/${key}`) && this.currentUrl.includes(`kind=${kind}`);
    if (key === 'home-blocks') return ['home-blocks', 'home-features', 'hero-slides'].some(value => this.currentUrl.includes(`/content/${value}`));
    return this.currentUrl.includes(`/content/${key}`);
  }
  initials(name: string): string { return name.split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase(); }
  signOut(): void { this.api.logout().subscribe(() => this.router.navigate(['/login'])); }
}
