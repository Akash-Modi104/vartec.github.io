import { Component, OnInit, OnDestroy, Renderer2, ViewChild } from '@angular/core';
import { MatMenuTrigger } from '@angular/material';
@Component({
  selector: 'app-hero2',
  templateUrl: './hero2.component.html',
  styleUrls: ['./hero2.component.css']
})
export class Hero2Component implements  OnInit, OnDestroy {
  videoElement:any;
  videoSources: string[];
  currentVideoIndex: number;
  backgroundImages: string[];
  currentBackgroundIndex: number;
  backgroundInterval: any;
 

  selectedItem: string = '';

  selectItem(item: string) {
    this.selectedItem = item;
    // Optionally, you might want to close the currently open menu
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