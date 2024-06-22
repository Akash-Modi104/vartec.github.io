import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-servives-rotating',
  templateUrl: './servives-rotating.component.html',
  styleUrls: ['./servives-rotating.component.css']
})
export class ServivesRotatingComponent implements OnInit, OnDestroy {
  panels = [
    {
      image: "assets/image/services/e&m/engineering procurement and construction (EPC).jpg",
      title: 'EPC_TITLE',
      description: 'EPC_DESC',
      route: 'services/epc'
    },
    {
      image: "assets/image/services/Consulting services/design CAD.jpg",
      title: 'CONSULTING_SERVICES_TITLE',
      description: 'CONSULTING_SERVICES_DESC',
      route: 'services/Consulting'
    },
    {
      image: "assets/image/services/Operation and Maintenance/OM services.jpg",
      title: 'OPERATION_AND_MAINTENANCE_TITLE',
      description: 'OPERATION_AND_MAINTENANCE_DESC',
      route: 'services/operationmaintenance'
    }
  ];

  customOptions = {
    loop: true,
    margin: 10,
    nav: true,
    dots: true,
    autoplay: true,
    autoplayTimeout: 3000,
    responsive: {
      0: {
        items: 1
      },
      600: {
        items: 2
      },
      1000: {
        items: 3
      }
    }
  };

  languageChangeSubscription: Subscription;

  constructor(
    private router: Router,
    private translate: TranslateService,
    private languageService: LanguageService
  ) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      this.updateContent();
    });
  }

  ngOnInit(): void {
    // Implement any initialization logic if needed
  }

  ngOnDestroy(): void {
    if (this.languageChangeSubscription) {
      this.languageChangeSubscription.unsubscribe();
    }
  }

  updateContent(): void {
    // Handle any content updates needed on language change
  }

  navigateToService(route: string): void {
    this.router.navigate([route]);
  }
}
