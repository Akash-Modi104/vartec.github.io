import { Component, OnInit, OnDestroy, Renderer2, ElementRef, ViewChild, HostListener } from '@angular/core';

@Component({
  selector: 'app-hero2',
  templateUrl: './hero2.component.html',
  styleUrls: ['./hero2.component.css']
})
export class Hero2Component implements OnInit, OnDestroy {
  videoElement:any;
  @ViewChild('heroElement', { static: true }) heroElement!: ElementRef;
  videoSources: string[];
  currentVideoIndex: number;
  backgroundImages: string[];
  currentBackgroundIndex: number;
  backgroundInterval: any;
  toshow = false;

  activeMenu: string | null = null;
  selectedItem: string | null = null;

  toggleDropdown(menu: string) {
    this.activeMenu = this.activeMenu === menu ? null : menu;
    if (menu === 'homeMenu') {
      this.toshow = false;
    }
  }

  selectItem(item: string) {
    this.selectedItem = item;
    this.activeMenu = null;
    this.toshow = true;
  }

  constructor(private renderer: Renderer2) {
    this.videoSources = [
      'assets/video/video2.mov',
      'assets/video/video1.mov',
      'assets/video/video3.mov'
    ];
    this.currentVideoIndex = 0;

    this.backgroundImages = [
      'assets/image/hero.jpg',
      'assets/image/hero1.jpg',
      'assets/image/hero3-min.jpg'
    ];
    this.currentBackgroundIndex = 0;
  }

  ngOnInit() {
    // this.videoElement = document.getElementById('aboutVideo') as HTMLVideoElement;
    // this.videoElement.src = this.videoSources[this.currentVideoIndex];
    // this.videoElement.play();
    
    // this.videoElement.addEventListener('ended', this.handleVideoEnded.bind(this));

    // Start background image change interval
    this.backgroundInterval = setInterval(this.changeBackgroundImage.bind(this), 3000);
  }

  ngOnDestroy() {
    if (this.backgroundInterval) {
      clearInterval(this.backgroundInterval);
    }
  }

  handleVideoEnded() {
    this.currentVideoIndex = (this.currentVideoIndex + 1) % this.videoSources.length;
    this.videoElement.src = this.videoSources[this.currentVideoIndex];
    this.videoElement.play();
  }

  changeBackgroundImage() {
    this.currentBackgroundIndex = (this.currentBackgroundIndex + 1) % this.backgroundImages.length;
    const heroElement = document.querySelector('.hero');
    if (heroElement) {
      this.renderer.setStyle(heroElement, 'background-image', `url(${this.backgroundImages[this.currentBackgroundIndex]})`);
    }
  }


  @HostListener('document:click', ['$event'])
  handleClick(event: Event) {
    const target = event.target as HTMLElement;
    const isDropdownButton = target.classList.contains('dropdown-btn') || target.closest('.dropdown-menu');
    if (!isDropdownButton) {
      this.activeMenu = null;
    }
  }
}