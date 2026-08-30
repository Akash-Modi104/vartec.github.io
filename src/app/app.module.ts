import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule,ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; 


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FooterComponent } from './footer/footer.component';
import { ContactComponent } from './contact/contact.component';
import { Hero2Component } from './hero2/hero2.component';
import { EpcComponent } from './services/epc/epc.component';
import { ConsultaingComponent } from './services/consultaing/consultaing.component';
import { OpertaionComponent } from './services/opertaion/opertaion.component';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { BatterystorageComponent } from './projects/batterystorage/batterystorage.component';
import { CarpotsComponent } from './projects/carpots/carpots.component';
import { EvchargingComponent } from './projects/evcharging/evcharging.component';
import { FloatingsolarComponent } from './projects/floatingsolar/floatingsolar.component';
import { SecuritysystemComponent } from './projects/securitysystem/securitysystem.component';
import { SolarparksComponent } from './projects/solarparks/solarparks.component';
import { ToastrModule } from 'ngx-toastr';
import { HomeComponent } from './home.component';

export function HttpLoaderFactory(http: HttpClient): TranslateHttpLoader {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
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

   
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'serverApp' }),
    AppRoutingModule,
    FormsModule, 
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    ToastrModule.forRoot(), 

    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
