import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AboutUsComponent } from './home/about-us/about-us.component';
import { EpcComponent } from './services/epc/epc.component';
import { ConsultaingComponent } from './services/consultaing/consultaing.component';
import { OpertaionComponent } from './services/opertaion/opertaion.component';

const routes: Routes = [
 
  { path: '', redirectTo: '/', pathMatch: 'full' },
    { path: 'home/about_us', component: AboutUsComponent },
    { path: 'services/epc', component: EpcComponent },
    { path: 'services/Consulting', component: ConsultaingComponent },
    { path: 'services/operationmaintenance', component: OpertaionComponent },
 
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
