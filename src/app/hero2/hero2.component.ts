import { DOCUMENT } from '@angular/common';
import { Component, HostListener, Inject, OnDestroy, OnInit } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { LanguageService } from '../language.service';

@Component({
  selector: 'app-hero2',
  templateUrl: './hero2.component.html',
  styleUrls: ['./hero2.component.css']
})
export class Hero2Component implements OnInit, OnDestroy {
  readonly backgroundImages = [
    'assets/image/hero1-min.webp',
    'assets/image/hero2-min.webp',
    'assets/image/hero3-min.webp',
    'assets/image/hero4-min.webp',
    'assets/image/hero5-min.webp',
    'assets/image/hero6-min.webp',
    'assets/image/hero7-min.webp'
  ];

  private readonly siteUrl = 'https://akash-modi104.github.io/vartec.github.io/';
  private readonly defaultTitle = 'Solar EPC, Battery Storage & O&M in the UK | VARTEC';
  private readonly defaultDescription = 'VARTEC designs, builds and maintains large-scale solar PV, battery storage, solar carports and EV charging projects across the UK and the Netherlands.';

  currentBackgroundIndex = 0;
  backgroundImage = this.backgroundImages[0];
  backgroundInterval?: ReturnType<typeof setInterval>;
  imageCache: HTMLImageElement[] = [];
  toshow = false;
  toshowlan = true;
  showMiddleSection = false;
  fullView = false;
  activeMenu: string | null = null;
  selectedItem: string | null = null;
  isMenuOpen = false;

  private readonly languageChangeSubscription: Subscription;
  private readonly navigationSubscription: Subscription;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private languageService: LanguageService,
    private translate: TranslateService,
    private title: Title,
    private meta: Meta,
    @Inject(DOCUMENT) private document: Document
  ) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(event => {
      this.toshowlan = event.lang !== 'nl';
      this.document.documentElement.lang = event.lang === 'nl' ? 'nl-NL' : 'en-GB';
    });

    this.navigationSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.updatePageState();
        this.configureHeroRotation();
        this.closeMenu();
      });
  }

  ngOnInit() {
    this.languageService.setInitialAppLanguage();
    this.toshowlan = this.translate.currentLang !== 'nl';
  }

  ngOnDestroy() {
    this.stopHeroRotation();
    this.languageChangeSubscription.unsubscribe();
    this.navigationSubscription.unsubscribe();
  }

  private updatePageState() {
    const currentRoute = this.route.snapshot.firstChild;
    const routeData = currentRoute?.data ?? {};
    const currentPath = this.router.url.split(/[?#]/)[0];
    this.fullView = routeData['fullView'] ?? currentPath === '/';
    this.showMiddleSection = this.fullView;
    this.updateHeroPreload();

    const pageTitle = routeData['seoTitle'] ?? this.defaultTitle;
    const description = routeData['seoDescription'] ?? this.defaultDescription;
    const routePath = this.router.url.split(/[?#]/)[0].replace(/^\//, '').replace(/\/$/, '');
    const canonicalUrl = routePath ? `${this.siteUrl}${routePath}/` : this.siteUrl;

    this.title.setTitle(pageTitle);
    this.meta.updateTag({ name: 'description', content: description });
    this.meta.updateTag({ name: 'robots', content: 'index, follow, max-image-preview:large' });
    this.meta.updateTag({ property: 'og:type', content: 'website' });
    this.meta.updateTag({ property: 'og:site_name', content: 'VARTEC' });
    this.meta.updateTag({ property: 'og:title', content: pageTitle });
    this.meta.updateTag({ property: 'og:description', content: description });
    this.meta.updateTag({ property: 'og:url', content: canonicalUrl });
    this.meta.updateTag({ property: 'og:image', content: `${this.siteUrl}assets/image/hero3-min.webp` });
    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.updateCanonicalUrl(canonicalUrl);
  }

  private updateCanonicalUrl(url: string) {
    let canonical = this.document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!canonical) {
      canonical = this.document.createElement('link');
      canonical.rel = 'canonical';
      this.document.head.appendChild(canonical);
    }
    canonical.href = url;
  }

  private updateHeroPreload() {
    let preload = this.document.head.querySelector<HTMLLinkElement>('link[data-vartec-hero-preload]');
    if (!this.showMiddleSection) {
      preload?.remove();
      return;
    }

    if (!preload) {
      preload = this.document.createElement('link');
      preload.rel = 'preload';
      preload.as = 'image';
      preload.setAttribute('fetchpriority', 'high');
      preload.setAttribute('data-vartec-hero-preload', '');
      this.document.head.appendChild(preload);
    }
    preload.href = this.backgroundImages[0];
  }

  private configureHeroRotation() {
    if (!this.showMiddleSection || typeof window === 'undefined') {
      this.stopHeroRotation();
      return;
    }

    this.preloadNextImage();
    if (!this.backgroundInterval) {
      this.backgroundInterval = setInterval(() => this.changeBackgroundImage(), 6000);
    }
  }

  private stopHeroRotation() {
    if (this.backgroundInterval) {
      clearInterval(this.backgroundInterval);
      this.backgroundInterval = undefined;
    }
  }

  private preloadNextImage() {
    if (typeof Image === 'undefined') {
      return;
    }

    const nextIndex = (this.currentBackgroundIndex + 1) % this.backgroundImages.length;
    if (!this.imageCache[nextIndex]) {
      const image = new Image();
      image.decoding = 'async';
      image.src = this.backgroundImages[nextIndex];
      this.imageCache[nextIndex] = image;
    }
  }

  changeBackgroundImage() {
    this.currentBackgroundIndex = (this.currentBackgroundIndex + 1) % this.backgroundImages.length;
    this.backgroundImage = this.backgroundImages[this.currentBackgroundIndex];
    this.preloadNextImage();
  }

  toggleDropdown(menu: string) {
    this.activeMenu = this.activeMenu === menu ? null : menu;
  }

  closeMenu() {
    this.activeMenu = null;
    this.isMenuOpen = false;
  }

  selectItem(item: string) {
    this.selectedItem = item;
    this.toshow = true;
    this.closeMenu();
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  switchLanguage(language: string) {
    this.languageService.switchLanguage(language);
    this.closeMenu();
  }

  scrollToSection(section: string) {
    const element = this.document.getElementById(section);
    element?.scrollIntoView({ behavior: 'smooth' });
    this.closeMenu();
  }

  toggleMenu(event: MouseEvent) {
    event.stopPropagation();
    this.isMenuOpen = !this.isMenuOpen;
    if (!this.isMenuOpen) {
      this.activeMenu = null;
    }
  }

  @HostListener('document:click', ['$event'])
  handleClick(event: Event) {
    const target = event.target as HTMLElement;
    const isNavigationInteraction = target.closest('.navbar');
    if (!isNavigationInteraction) {
      this.closeMenu();
    }
  }

  @HostListener('document:keydown.escape')
  handleEscape() {
    this.closeMenu();
  }
}
