import { isPlatformBrowser } from '@angular/common';
import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private readonly STORAGE_KEY = 'vartecpreferredLanguage';

  constructor(private translate: TranslateService, @Inject(PLATFORM_ID) private platformId: object) { }

  switchLanguage(language: string) {
    this.translate.use(language);
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem(this.STORAGE_KEY, language);
    }
  }

  getStoredLanguage(): string | null {
    return isPlatformBrowser(this.platformId) ? localStorage.getItem(this.STORAGE_KEY) : null;
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
