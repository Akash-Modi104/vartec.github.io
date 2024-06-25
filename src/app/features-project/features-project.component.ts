import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-features-project',
  templateUrl: './features-project.component.html',
  styleUrls: ['./features-project.component.css']
})
export class FeaturesProjectComponent implements OnInit {
  projects = [
    { title: 'Battery Storage', image: 'assets/project/Battery storage/battery storage.jpg', description: '12MW/24MWh Battery Storage System' },
    { title: 'Energy Storage', image: 'assets/project/Battery storage/Energy-storage-on-page-1-scaled.jpg', description: '6MW/12MWh Battery Storage System' },
    { title: 'Solar with Storage', image: 'assets/project/Battery storage/Solar with storage.jpg', description: 'Solar with Storage System' },
    { title: 'Generic Storage', image: 'assets/project/Battery storage/Solar with storage.webp', description: 'Generic 1MW Battery Storage Unit' }
  ];

  currentIndex = 0;

  constructor() {}

  ngOnInit(): void {}

  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }

  next() {
    if (this.currentIndex < this.projects.length - 1) {
      this.currentIndex++;
    }
  }
}