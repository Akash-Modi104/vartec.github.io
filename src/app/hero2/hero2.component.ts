import { Component, OnInit, OnDestroy, ElementRef, ViewChild, HostListener, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../language.service';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-hero2',
  templateUrl: './hero2.component.html',
  styleUrls: ['./hero2.component.css']
})
export class Hero2Component implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('heroElement', { static: true }) heroElement!: ElementRef;
  @ViewChild('aboutUsElement', { static: true }) aboutUsElement!: ElementRef;
  backgroundImages: string[];
  currentBackgroundIndex: number;
  backgroundInterval: any;
  toshow = false;
  toshowlan = true;
  showMiddleSection = true;
  languageChangeSubscription: Subscription;
  fullView = true;
  backgroundImage: string;
  imageCache: HTMLImageElement[] = []; // Image cache for preloading

  activeMenu: string | null = null;
  selectedItem: string | null = null;
  isMenuOpen: boolean = false;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private languageService: LanguageService,
    private translate: TranslateService,
    private cdr: ChangeDetectorRef // Inject ChangeDetectorRef
  ) {
    this.backgroundImages = [
      'assets/image/hero1-min.jpg',
      'assets/image/hero2-min.jpg',
      'assets/image/hero3-min.jpg',
      'assets/image/hero4-min.jpg',
      'assets/image/hero5-min.jpg',
      'assets/image/hero6-min.jpg',
      'assets/image/hero7-min.jpg'
    ];
    this.currentBackgroundIndex = 0;
    this.backgroundImage = this.backgroundImages[this.currentBackgroundIndex];
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      console.log('Language changed');
    });

    this.router.events.pipe(filter(event => event instanceof NavigationEnd)).subscribe(() => {
      const currentRoute = this.route.snapshot.firstChild;
      this.fullView = currentRoute ? currentRoute.data['fullView'] : true;
      this.showMiddleSection = this.fullView;
      this.activeMenu = null; // Ensure no dropdown is shown by default
    });
  }

  ngOnInit() {
    const currentRoute = this.route.snapshot.firstChild;
    this.fullView = currentRoute ? currentRoute.data['fullView'] : true;
    this.showMiddleSection = this.fullView;

    // Set the initial language
    this.languageService.setInitialAppLanguage();
    // Set the flag for showing language toggle
    this.toshowlan = this.translate.currentLang !== 'nl';

    // Preload all background images
    this.preloadImages();

    // Initialize background image interval
    this.backgroundInterval = setInterval(() => {
      this.changeBackgroundImage();
    }, 4000);
  }

  ngAfterViewInit() {
    // Ensure initial background image is set correctly
    this.changeBackgroundImage();
  }

  ngOnDestroy() {
    if (this.backgroundInterval) {
      clearInterval(this.backgroundInterval);
    }
    if (this.languageChangeSubscription) {
      this.languageChangeSubscription.unsubscribe();
    }
  }

  preloadImages() {
    this.backgroundImages.forEach((src, index) => {
      const img = new Image();
      img.src = src;
      this.imageCache[index] = img;
    });
  }

  changeBackgroundImage() {
    this.currentBackgroundIndex = (this.currentBackgroundIndex + 1) % this.backgroundImages.length;
    this.backgroundImage = this.backgroundImages[this.currentBackgroundIndex];
    this.cdr.detectChanges(); // Trigger change detection manually
    console.log(`Background image set to: ${this.backgroundImage}`);
  }

  onImageError(event: Event) {
    console.error(`Failed to load image: ${this.backgroundImage}`);
    this.backgroundImage = 'assets/image/default-background.jpg'; // Fallback image
    this.cdr.detectChanges();
  }

  toggleDropdown(menu: string) {
    this.activeMenu = this.activeMenu === menu ? null : menu;

    if (menu === 'homeMenu') {
      this.toshow = false;
      this.showMiddleSection = true;
    } else if (menu === 'projectsMenu' || menu === 'servicesMenu') {
      // Do nothing for projectsMenu and servicesMenu
    } else {
      this.toshow = true;
      this.showMiddleSection = false;
    }

    // Only scroll to top if a dropdown is being opened and it's not projects or services menu
    if (this.activeMenu && menu !== 'projectsMenu' && menu !== 'servicesMenu') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  selectItem(item: string) {
    this.selectedItem = item;
    this.activeMenu = null;
    this.isMenuOpen = false; // Close the menu on selection
    this.updateHamburgerMenu(); // Update the hamburger menu icon state
    this.toshow = true;
    this.showMiddleSection = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  switchLanguage(language: string) {
    this.languageService.switchLanguage(language);
    this.toshowlan = language !== 'nl';
  }

  scrollToSection(section: string) {
    let element: HTMLElement | null = null;
    switch (section) {
      case 'aboutUsSection':
        element = document.getElementById('aboutUsSection');
        break;
      case 'contactussection':
        element = document.getElementById('contactussection');
        break;
    }
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    this.isMenuOpen = false; // Close the menu on navigation
    this.updateHamburgerMenu(); // Update the hamburger menu icon state
  }

  navigateTo(route: string) {
    this.router.navigate([route]).then(() => {
      this.isMenuOpen = false; // Close the menu on navigation
      this.activeMenu = null; // Ensure no dropdown is shown by default
      this.updateHamburgerMenu(); // Update the hamburger menu icon state
    });
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen; // Toggle the menu open state
    this.updateHamburgerMenu(); // Update the hamburger menu icon state
  }

  updateHamburgerMenu() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    if (this.isMenuOpen) {
      hamburgerMenu?.classList.add('active');
    } else {
      hamburgerMenu?.classList.remove('active');
    }
  }

  @HostListener('document:click', ['$event'])
  handleClick(event: Event) {
    const target = event.target as HTMLElement;
    const isDropdownButton = target.classList.contains('dropdown-btn') || target.closest('.dropdown-menu');
    if (!isDropdownButton) {
      this.activeMenu = null;
      this.isMenuOpen = false; // Close the menu if clicked outside
      this.updateHamburgerMenu(); // Update the hamburger menu icon state
    }
  }
}
