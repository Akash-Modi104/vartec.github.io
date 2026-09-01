import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, map, shareReplay, tap } from 'rxjs/operators';
import { CmsUser, DashboardResponse, DetailResponse, ResourceResponse, SessionResponse } from './models';

@Injectable({ providedIn: 'root' })
export class CmsApiService {
  private readonly base = '/cms-api';
  private sessionRequest?: Observable<SessionResponse>;
  readonly user$ = new BehaviorSubject<CmsUser | null>(null);

  constructor(private http: HttpClient) {}

  session(force = false): Observable<SessionResponse> {
    if (!this.sessionRequest || force) {
      this.sessionRequest = this.http.get<SessionResponse>(`${this.base}/session/`).pipe(
        tap(response => this.user$.next(response.authenticated && response.user ? response.user : null)),
        catchError(() => {
          this.user$.next(null);
          return of({ authenticated: false });
        }),
        shareReplay(1)
      );
    }
    return this.sessionRequest;
  }

  login(username: string, password: string): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.base}/login/`, { username, password }).pipe(
      tap(response => {
        this.sessionRequest = undefined;
        this.user$.next(response.user || null);
      })
    );
  }

  logout(): Observable<void> {
    return this.http.post<SessionResponse>(`${this.base}/logout/`, {}).pipe(
      tap(() => {
        this.sessionRequest = undefined;
        this.user$.next(null);
      }),
      map(() => void 0)
    );
  }

  dashboard(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(`${this.base}/dashboard/`);
  }

  list(resource: string, query = '', page = 1): Observable<ResourceResponse> {
    let params = new HttpParams().set('page', page).set('pageSize', 50);
    if (query) params = params.set('q', query);
    return this.http.get<ResourceResponse>(`${this.base}/resources/${resource}/`, { params });
  }

  detail(resource: string, id: number): Observable<DetailResponse> {
    return this.http.get<DetailResponse>(`${this.base}/resources/${resource}/${id}/`);
  }

  create(resource: string, payload: FormData): Observable<{ item: any }> {
    return this.http.post<{ item: any }>(`${this.base}/resources/${resource}/`, payload);
  }

  update(resource: string, id: number, payload: FormData | Record<string, any>): Observable<{ item: any }> {
    if (payload instanceof FormData) {
      return this.http.post<{ item: any }>(`${this.base}/resources/${resource}/${id}/`, payload);
    }
    return this.http.patch<{ item: any }>(`${this.base}/resources/${resource}/${id}/`, payload);
  }

  delete(resource: string, id: number): Observable<{ deleted: boolean }> {
    return this.http.delete<{ deleted: boolean }>(`${this.base}/resources/${resource}/${id}/`);
  }
}
