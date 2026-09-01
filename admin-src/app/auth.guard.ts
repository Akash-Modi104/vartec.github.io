import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { CmsApiService } from './cms-api.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private api: CmsApiService, private router: Router) {}
  canActivate(): Observable<boolean | UrlTree> {
    return this.api.session().pipe(map(session => session.authenticated ? true : this.router.createUrlTree(['/login'])));
  }
}
