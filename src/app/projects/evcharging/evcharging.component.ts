import { Component, OnInit } from '@angular/core';
import { TranslateService, LangChangeEvent } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-evcharging',
  templateUrl: './evcharging.component.html',
  styleUrls: ['./evcharging.component.css']
})
export class EvchargingComponent implements OnInit {

  languageChangeSubscription: Subscription;
 



  constructor(private languageService: LanguageService, private translate: TranslateService) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      this.updateContent();
    
    });
  }
  updateContent() {
    throw new Error('Method not implemented.');
  }

  ngOnInit(): void {
  }

}

