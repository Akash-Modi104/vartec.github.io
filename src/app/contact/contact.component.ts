// src/app/contact/contact.component.ts
import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { ConfigService } from 'src/app/config.service';
import { Subscription } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent {
  languageChangeSubscription: Subscription;

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private configService: ConfigService,
    private http: HttpClient
  ) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      console.log('language changed');
    });
  }

  contact = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    message: ''
  };



  
  sendEmail(contactForm: { valid: any; }) {
    if (contactForm.valid) {
      const headers = new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' });
      const body = `firstName=${this.contact.firstName}&lastName=${this.contact.lastName}&email=${this.contact.email}&phone=${this.contact.phone}&message=${this.contact.message}`;

      this.http.post('send_mail.php', body, { headers, responseType: 'text' }).subscribe(
        (response) => {
          console.log('Success', response);
        },
        (error) => {
          console.error('Error', error);
        }
      );
    }
  }
}