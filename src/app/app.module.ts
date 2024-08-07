import { NgModule,CUSTOM_ELEMENTS_SCHEMA  } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule,ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; 
import { MatIconModule } from '@angular/material/icon';


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FooterComponent } from './footer/footer.component';
import { ContactComponent } from './contact/contact.component';
import { Hero2Component } from './hero2/hero2.component';
import {MatMenuModule} from '@angular/material/menu';
import {MatButtonModule} from '@angular/material/button';
import { EpcComponent } from './services/epc/epc.component';
import { ConsultaingComponent } from './services/consultaing/consultaing.component';
import { OpertaionComponent } from './services/opertaion/opertaion.component';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { CarouselModule } from 'ngx-owl-carousel-o';
import { MatDialogModule } from '@angular/material/dialog';
import { BatterystorageComponent } from './projects/batterystorage/batterystorage.component';
import { CarpotsComponent } from './projects/carpots/carpots.component';
import { EvchargingComponent } from './projects/evcharging/evcharging.component';
import { FloatingsolarComponent } from './projects/floatingsolar/floatingsolar.component';
import { SecuritysystemComponent } from './projects/securitysystem/securitysystem.component';
import { SolarparksComponent } from './projects/solarparks/solarparks.component';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ConfigService } from './config.service';
import { AlertDialogComponent } from './contact/alert-dialog/alert-dialog.component';
import { ToastrModule } from 'ngx-toastr';

export function HttpLoaderFactory(http: HttpClient): TranslateHttpLoader {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

@NgModule({
  declarations: [
    AppComponent,
    FooterComponent,
    ContactComponent,
    Hero2Component,
    EpcComponent,
    ConsultaingComponent,
    OpertaionComponent,

    BatterystorageComponent,
    CarpotsComponent,
    EvchargingComponent,
    FloatingsolarComponent,
    SecuritysystemComponent,

    SolarparksComponent,
      AlertDialogComponent,

   
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'serverApp' }),
    MatIconModule,
    AppRoutingModule,
    FormsModule, 
    MatMenuModule,
    MatButtonModule,BrowserAnimationsModule,
    HttpClientModule,
    CarouselModule,
    MatCardModule,
    ReactiveFormsModule,
    MatToolbarModule,
    MatDialogModule,
    ToastrModule.forRoot(), 

    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }
    })
  ],
  providers: [ConfigService],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class AppModule { }
