import { Component, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import { CmsApiService } from './cms-api.service';

interface NavItem { key: string; label: string; mark: string; }
interface NavGroup { label: string; items: NavItem[]; }

@Component({ selector: 'cms-root', templateUrl: './app.component.html' })
export class AppComponent implements OnInit {
  mobileOpen = false;
  currentUrl = this.router.url;
  readonly user$ = this.api.user$;
  readonly groups: NavGroup[] = [
    { label: 'Content', items: [{ key: 'pages', label: 'Pages', mark: 'PG' }, { key: 'sections', label: 'Page sections', mark: 'SC' }, { key: 'text', label: 'Website text', mark: 'TX' }] },
    { label: 'Homepage', items: [{ key: 'hero-slides', label: 'Hero slides', mark: 'HS' }, { key: 'home-blocks', label: 'Content blocks', mark: 'BL' }, { key: 'home-features', label: 'Feature cards', mark: 'FC' }] },
    { label: 'Manage', items: [{ key: 'media', label: 'Media library', mark: 'MD' }, { key: 'enquiries', label: 'Enquiries', mark: 'EN' }, { key: 'settings', label: 'Appearance', mark: 'AP' }] }
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
  isActive(key: string): boolean { return this.currentUrl.includes(`/content/${key}`); }
  initials(name: string): string { return name.split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase(); }
  signOut(): void { this.api.logout().subscribe(() => this.router.navigate(['/login'])); }
}
