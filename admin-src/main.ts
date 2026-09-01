import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AdminModule } from './app/admin.module';

platformBrowserDynamic().bootstrapModule(AdminModule).catch(error => console.error(error));
