import {CanActivate, Router} from '@angular/router';
import {ApiClientService} from './services/api-client.service';
import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private api: ApiClientService, private router: Router) {
  }

  canActivate() {
    // console.log(this.api.hasToken())
    if (this.api.hasToken()) {
      return true;
    }

    this.router.navigate(['/sign-in/']);

    return false;
  }
}
