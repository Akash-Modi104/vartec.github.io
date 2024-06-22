import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private readonly STORAGE_KEY = 'vartecpreferredLanguage';

  constructor(private translate: TranslateService) { }

  switchLanguage(language: string) {
    this.translate.use(language);
    localStorage.setItem(this.STORAGE_KEY, language);
  }

  getStoredLanguage(): string | null {
    return localStorage.getItem(this.STORAGE_KEY);
  }

  setInitialAppLanguage() {
    const storedLanguage = this.getStoredLanguage();
    if (storedLanguage) {
      this.translate.use(storedLanguage);
    } else {
      const browserLang = this.translate.getBrowserLang();
      if (browserLang && browserLang.match(/en|nl/)) {
        this.translate.setDefaultLang(browserLang);
      } else {
        this.translate.setDefaultLang('en');
      }
    }
  }
}
