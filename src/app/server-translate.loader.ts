import { Injectable } from '@angular/core';
import { TranslateLoader } from '@ngx-translate/core';
import { Observable, of } from 'rxjs';
import { readFileSync } from 'fs';
import { join } from 'path';

@Injectable()
export class ServerTranslateLoader implements TranslateLoader {
  getTranslation(language: string): Observable<Record<string, string>> {
    const translationFile = join(process.cwd(), 'src', 'assets', 'i18n', `${language}.json`);
    const translations = JSON.parse(readFileSync(translationFile, 'utf8')) as Record<string, string>;
    return of(translations);
  }
}
