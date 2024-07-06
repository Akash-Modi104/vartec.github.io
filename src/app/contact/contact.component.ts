// src/app/contact/contact.component.ts
import { Component } from '@angular/core';
import emailjs, { EmailJSResponseStatus } from 'emailjs-com';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { ConfigService } from 'src/app/config.service';
import { Subscription } from 'rxjs';

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
    private configService: ConfigService
  ) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      console.log('language changed');
    });
  }

  sendEmail(contactForm: any) {
    const emailJsConfig = this.configService.getEmailJsConfig();

    emailjs.sendForm(
      emailJsConfig.serviceId,
      emailJsConfig.templateId,
      contactForm.form,
      emailJsConfig.userId
    ).then((result: EmailJSResponseStatus) => {
      console.log(result.text);
      alert('Your message has been sent successfully!');
    }, (error) => {
      console.log(error.text);
      alert('Oops! Something went wrong.');
    });
  }
}
