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

const routes: Routes = [
 
  { path: '', redirectTo: '/', pathMatch: 'full',data: { fullView: true }  },
  { path: 'services/epc', component: EpcComponent, data: { fullView: false } },
  { path: 'services/Consulting', component: ConsultaingComponent, data: { fullView: false } },
  { path: 'services/operationmaintenance', component: OpertaionComponent, data: { fullView: false } },
{ path: 'project/batterystorage', component: BatterystorageComponent, data: { fullView: false } },
{ path: 'project/carpots', component: CarpotsComponent, data: { fullView: false } },
{ path: 'project/batterystorage', component: BatterystorageComponent, data: { fullView: false } },
{ path: 'project/evcharging', component: EvchargingComponent, data: { fullView: false } }, // Add this
  { path: 'project/floating', component: FloatingsolarComponent, data: { fullView: false } }, // Add this
  { path: 'project/security', component: SecuritysystemComponent, data: { fullView: false } }, // Add this
  { path: 'project/solarparks', component: SolarparksComponent, data: { fullView: false } }, // Add this
  { path: '**', redirectTo: '/', pathMatch: 'full', data: { fullView: true } } // Redirect to home if path not available
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    initialNavigation: 'enabledBlocking'
})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
