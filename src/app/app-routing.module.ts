import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AboutUsComponent } from './home/about-us/about-us.component';
import { EpcComponent } from './services/epc/epc.component';
import { ConsultaingComponent } from './services/consultaing/consultaing.component';
import { OpertaionComponent } from './services/opertaion/opertaion.component';

const routes: Routes = [
 
  { path: '', redirectTo: '/', pathMatch: 'full',data: { fullView: true }  },
  { path: 'services/epc', component: EpcComponent, data: { fullView: false } },
  { path: 'services/Consulting', component: ConsultaingComponent, data: { fullView: false } },
  { path: 'services/operationmaintenance', component: OpertaionComponent, data: { fullView: false } }
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
