import { Component, OnInit } from '@angular/core';
import { TranslateService, LangChangeEvent } from '@ngx-translate/core';
import { LanguageService } from '../language.service';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent implements OnInit {
  currentYear: number = new Date().getFullYear();
  languageChangeSubscription: Subscription;

  constructor(private languageService: LanguageService, private translate: TranslateService, private router: Router) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      this.updateContent();
    });
  }

  ngOnInit(): void {}

  ngOnDestroy() {
    if (this.languageChangeSubscription) {
      this.languageChangeSubscription.unsubscribe();
    }
  }

  updateContent() {
    // Handle content updates on language change if necessary
  }

  scrollToSection(section: string) {
    if (this.router.url === '/') {
      const element = document.getElementById(section);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      this.router.navigate(['/']).then(() => {
        setTimeout(() => {
          const element = document.getElementById(section);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100); // Wait for navigation to complete
        });}}
    

  navigateAndScroll(route: string) {
    this.router.navigate([route]).then(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}