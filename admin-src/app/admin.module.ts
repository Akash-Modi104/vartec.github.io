import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HttpClientXsrfModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AdminRoutingModule } from './admin-routing.module';
import { AppComponent } from './app.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { EditorComponent } from './editor/editor.component';
import { LoginComponent } from './login/login.component';
import { ResourceListComponent } from './resource-list/resource-list.component';

@NgModule({
  declarations: [AppComponent, DashboardComponent, EditorComponent, LoginComponent, ResourceListComponent],
  imports: [BrowserModule, FormsModule, ReactiveFormsModule, HttpClientModule, HttpClientXsrfModule.withOptions({ cookieName: 'csrftoken', headerName: 'X-CSRFToken' }), AdminRoutingModule],
  bootstrap: [AppComponent]
})
export class AdminModule {}
