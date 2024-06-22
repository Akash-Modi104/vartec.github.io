import { Component, OnInit } from '@angular/core';
import { TranslateService, LangChangeEvent } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-consultaing',
  templateUrl: './consultaing.component.html',
  styleUrls: ['./consultaing.component.css']
})
export class ConsultaingComponent implements OnInit {
  languageChangeSubscription: Subscription;
  backgroundImageUrl: string = 'assets/image/services/Consulting services/health and safety.jpg';



  constructor(private languageService: LanguageService, private translate: TranslateService) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      this.updateContent();
      this.backgroundImageUrl = 'assets/image/services/Consulting services/health and safety.jpg';
    });
  }
  updateContent() {
    throw new Error('Method not implemented.');
  }

  ngOnInit(): void {
  }

}
