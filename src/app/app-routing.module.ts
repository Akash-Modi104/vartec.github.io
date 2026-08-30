import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EpcComponent } from './services/epc/epc.component';
import { ConsultaingComponent } from './services/consultaing/consultaing.component';
import { OpertaionComponent } from './services/opertaion/opertaion.component';
import { BatterystorageComponent } from './projects/batterystorage/batterystorage.component';
import { CarpotsComponent } from './projects/carpots/carpots.component';
import { EvchargingComponent } from './projects/evcharging/evcharging.component';
import { FloatingsolarComponent } from './projects/floatingsolar/floatingsolar.component';
import { SecuritysystemComponent } from './projects/securitysystem/securitysystem.component';
import { SolarparksComponent } from './projects/solarparks/solarparks.component';
import { HomeComponent } from './home.component';

const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: HomeComponent,
    data: {
      fullView: true,
      seoTitle: 'Solar EPC, Battery Storage & O&M in the UK | VARTEC',
      seoDescription: 'VARTEC designs, builds and maintains large-scale solar PV, battery storage, solar carports and EV charging projects across the UK and the Netherlands.'
    }
  },
  {
    path: 'services/epc',
    component: EpcComponent,
    data: {
      fullView: false,
      seoTitle: 'Solar EPC Services in the UK | VARTEC',
      seoDescription: 'Engineering, procurement and construction services for utility-scale solar PV, battery storage and EV infrastructure projects across the UK.'
    }
  },
  {
    path: 'services/consulting',
    component: ConsultaingComponent,
    data: {
      fullView: false,
      seoTitle: 'Solar Energy Consulting Services UK | VARTEC',
      seoDescription: 'Solar project design, programme management, health and safety coordination and construction management for renewable energy projects in the UK.'
    }
  },
  {
    path: 'services/operation-maintenance',
    component: OpertaionComponent,
    data: {
      fullView: false,
      seoTitle: 'Solar Operation & Maintenance Services UK | VARTEC',
      seoDescription: 'Professional solar PV operation and maintenance, testing, monitoring, cleaning and asset support for UK solar energy installations.'
    }
  },
  {
    path: 'project/battery-storage',
    component: BatterystorageComponent,
    data: {
      fullView: false,
      seoTitle: 'Battery Storage Projects UK & Europe | VARTEC',
      seoDescription: 'Explore VARTEC battery energy storage projects, including multi-megawatt systems and integrated solar-plus-storage installations.'
    }
  },
  {
    path: 'project/carports',
    component: CarpotsComponent,
    data: {
      fullView: false,
      seoTitle: 'Solar Carport Projects UK & Europe | VARTEC',
      seoDescription: 'Explore VARTEC commercial solar carport projects with integrated renewable power generation and EV charging infrastructure.'
    }
  },
  {
    path: 'project/ev-charging',
    component: EvchargingComponent,
    data: {
      fullView: false,
      seoTitle: 'Commercial EV Charging Projects | VARTEC UK',
      seoDescription: 'Commercial EV charging solutions integrated with solar carports and renewable energy infrastructure for UK and European projects.'
    }
  },
  {
    path: 'project/floating-solar',
    component: FloatingsolarComponent,
    data: {
      fullView: false,
      seoTitle: 'Floating Solar Projects UK & Europe | VARTEC',
      seoDescription: 'View VARTEC floating solar PV installations and operation and maintenance work for multi-megawatt renewable energy projects.'
    }
  },
  {
    path: 'project/security-systems',
    component: SecuritysystemComponent,
    data: {
      fullView: false,
      seoTitle: 'Solar Farm Security Systems UK | VARTEC',
      seoDescription: 'Security fencing, CCTV and radar-assisted PTZ camera systems designed to protect solar farms and renewable energy assets.'
    }
  },
  {
    path: 'project/solar-parks',
    component: SolarparksComponent,
    data: {
      fullView: false,
      seoTitle: 'Utility-Scale Solar Park Projects UK | VARTEC',
      seoDescription: 'Discover VARTEC solar parks in the UK and the Netherlands, including multi-megawatt design, construction and commissioning projects.'
    }
  },
  { path: 'services/Consulting', redirectTo: 'services/consulting', pathMatch: 'full' },
  { path: 'services/operationmaintenance', redirectTo: 'services/operation-maintenance', pathMatch: 'full' },
  { path: 'project/batterystorage', redirectTo: 'project/battery-storage', pathMatch: 'full' },
  { path: 'project/carpots', redirectTo: 'project/carports', pathMatch: 'full' },
  { path: 'project/evcharging', redirectTo: 'project/ev-charging', pathMatch: 'full' },
  { path: 'project/floating', redirectTo: 'project/floating-solar', pathMatch: 'full' },
  { path: 'project/security', redirectTo: 'project/security-systems', pathMatch: 'full' },
  { path: 'project/solarparks', redirectTo: 'project/solar-parks', pathMatch: 'full' },
  { path: '**', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { initialNavigation: 'enabledBlocking' })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
