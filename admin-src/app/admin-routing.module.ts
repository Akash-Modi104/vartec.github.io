import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';
import { DashboardComponent } from './dashboard/dashboard.component';
import { EditorComponent } from './editor/editor.component';
import { LoginComponent } from './login/login.component';
import { ResourceListComponent } from './resource-list/resource-list.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'content/:resource/new', component: EditorComponent, canActivate: [AuthGuard] },
  { path: 'content/:resource/:id', component: EditorComponent, canActivate: [AuthGuard] },
  { path: 'content/:resource', component: ResourceListComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: '' }
];

@NgModule({ imports: [RouterModule.forRoot(routes, { scrollPositionRestoration: 'top' })], exports: [RouterModule] })
export class AdminRoutingModule {}
