import { Component, OnInit, OnDestroy, Renderer2, ViewChild } from '@angular/core';
import { MatMenuTrigger } from '@angular/material';
import { TranslateService, LangChangeEvent } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-about-us',
  templateUrl: './about-us.component.html',
  styleUrls: ['./about-us.component.css']
})
export class AboutUsComponent implements OnInit {

  videoElement:any;
  videoSources: string[];
  currentVideoIndex: number;
  backgroundImages: string[];
  currentBackgroundIndex: number;
  backgroundInterval: any;
 

  activeMenu: string | null = null;
  selectedItem: string | null = null;

  toggleDropdown(menu: string) {
    this.activeMenu = this.activeMenu === menu ? null : menu;
  }

  selectItem(item: string) {
    this.selectedItem = item;
    this.activeMenu = null;
  }
  languageChangeSubscription: Subscription;



  constructor(private renderer: Renderer2,private languageService: LanguageService, private translate: TranslateService) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      this.updateContent();
    });
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
  updateContent() {
    throw new Error('Method not implemented.');
  }

  ngOnInit() {
    this.videoElement = document.getElementById('aboutVideo') as HTMLVideoElement;
    this.videoElement.src = this.videoSources[this.currentVideoIndex];
    this.videoElement.play();
    
    this.videoElement.addEventListener('ended', this.handleVideoEnded.bind(this));

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
}
