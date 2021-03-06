import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {BehaviorSubject, Observable, throwError} from 'rxjs';
import {LoaderIndicatorService} from './loader-indicator.service';
import {catchError, tap} from 'rxjs/operators';
import {MatSnackBar} from '@angular/material/snack-bar';

interface CredentialsRequest {
  username: string;
  password: string;
}

interface AuthResponse {
  token: string;
}

export interface IdentListItem {
  ident: string;
  version: string;
  last_seen_at: number;
  last_seen_from: string;
}

export declare type IdentListResponse = Array<IdentListItem>;

interface StatusResponseStatus {
  c: string;
  mod: string;
  subject: string;
  type: string;
  remaining: number;
  status: number;
  is_metric: boolean;
  updated_at: number;
}

interface StatusResponseItem {
  ident: string;
  agent_version: string;
  server_version: string;
  last_seen_at: number;
  last_seen_from: string;
  health: number;
  items: StatusResponseStatus[];
}

export declare type StatusResponse = Array<StatusResponseItem>;

interface MetricRecordSeries {
  [index: number]: number
}

interface MetricRecordSeriesCollection {
  min: MetricRecordSeries[];
  max: MetricRecordSeries[];
  avg: MetricRecordSeries[];
}

export interface MetricRecord {
  c: string,
  mod: string;
  subject: string;
  metric: string;
  format: string;
  series: MetricRecordSeriesCollection,
  min: number,
  max: number
}

export declare type MetricsResponse = Array<MetricRecord>;

export interface MetaRecord {
  ident: string;
  mod: string;
  updated_at: number;
  meta: object;
}

export declare type MetaResponse = Array<MetaRecord>;

export interface HealthResponseItem {
  ident: string,
  c: string;
  mod: string;
  subject: string;
  type: string;
  remaining: number;
  status: number;
  before: number;
  alert_sent: number;
  is_metric: boolean;
  last_seen_at: number;
  last_seen_from: string;
  updated_at: number;
}

export declare type HealthResponse = Array<HealthResponseItem>;

export interface VersionsResponse {
  server: string;
  web: string;
}

export interface KBNavItem {
  name: string;
  uri: string;
}

export interface KBNavCategory {
  name: string;
  items: KBNavItem[];
}

export interface KBNavView {
  default: {items: KBNavItem[]};
  categories: KBNavCategory[];
}

export interface KBArticle {
  markdown: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiClientService {
  isKnownUser: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(this.hasToken());
  private baseUrl = '/api';

  constructor(private http: HttpClient, private loader: LoaderIndicatorService, private snackbar: MatSnackBar) {
  }

  setToken(token: string): void {
    if (null === token) {
      window.localStorage.removeItem('token');
      this.isKnownUser.next(false);
      return;
    }

    window.localStorage.setItem('token', token);
    this.isKnownUser.next(true);
  }

  getToken(): string | null {
    const token = window.localStorage.getItem('token');
    return null === token || 0 === token.length ? null : token;
  }

  hasToken(): boolean {
    return null !== this.getToken();
  }

  signIn(credentials: CredentialsRequest) {
    return this.post<AuthResponse>('/sign-in/', credentials);
  }

  fetchVersions(): Observable<VersionsResponse> {
    return this.get<VersionsResponse>('/versions/');
  }

  fetchStatus(): Observable<StatusResponse> {
    return this.get<StatusResponse>('/status/');
  }

  fetchHealth(): Observable<HealthResponse> {
    return this.get<HealthResponse>('/health/');
  }

  fetchIdents(): Observable<IdentListResponse> {
    return this.get<IdentListResponse>('/ident/');
  }

  fetchMetrics(ident: string, period: string): Observable<MetricsResponse> {
    return this.get<MetricsResponse>('/metrics/' + ident + '/' + period + '/');
  }

  fetchMeta(ident: string): Observable<MetaResponse> {
    return this.get<MetaResponse>('/meta/' + ident + '/');
  }

  fetchKbNavigation(): Observable<KBNavView> {
    return this.get<KBNavView>('/kb/nav/');
  }

  fetchKBArticle(article): Observable<KBArticle> {
    return this.get<KBArticle>('/kb/article/' + article);
  }

  public post<T>(path: string, payload: any): Observable<T> {
    this.loader.inc();

    return this.http
      .post<T>(this.baseUrl + path, payload, {
        headers: {
          'x-auth-token': this.getToken() || ''
        }
      })
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(_ => this.loader.dec())
      );
  }

  private get<T>(path: string): Observable<T> {
    this.loader.inc();

    return this.http
      .get<T>(this.baseUrl + path, {
        headers: {
          'x-auth-token': this.getToken() || ''
        }
      })
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(_ => this.loader.dec())
      );
  }

  private handleError<T>(response: HttpErrorResponse): Observable<never> {
    this.loader.dec();

    if (response instanceof DOMException) {
      throw response;
    }

    let errorMessage = 'API failed - HTTP ' + response.status + ' - ' + response.statusText;
    if (response.error?.error) {
      errorMessage = response.error.error;
    }

    console.error(errorMessage);
    console.debug(response);

    this.snackbar.open(errorMessage, null, {
      duration: 3000,
      panelClass: 'error-alert',
      verticalPosition: 'top'
    });

    return throwError('Request failed');
  }
}
