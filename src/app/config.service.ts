// src/app/services/config.service.ts
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  getEmailJsConfig() {
    return {
      serviceId: this.getMetaContent('emailjs-service-id'),
      templateId: this.getMetaContent('emailjs-template-id'),
      userId: this.getMetaContent('emailjs-user-id')
    };
  }

  private getMetaContent(name: string): string {
    const element = document.querySelector(`meta[name='${name}']`);
    return element ? (element as HTMLMetaElement).content : '';
  }
}
