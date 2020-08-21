import {Component} from '@angular/core';
import {ApiClientService} from './services/api-client.service';
import {Router} from '@angular/router';
import {ViewUpdaterService} from './services/view-updater.service';
import {LoaderIndicatorService} from './services/loader-indicator.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  isKnownUser: boolean = this.api.isKnownUser.value;

  constructor(
    public api: ApiClientService,
    private router: Router,
    private viewUpdater: ViewUpdaterService,
    public loader: LoaderIndicatorService
  ) {
    api.isKnownUser.subscribe(it => {
      this.isKnownUser = it;
    });
  }

  signOut() {
    this.api.setToken(null);
    this.router.navigate(['/sign-in/']);
  }

  emitUpdateView() {
    this.viewUpdater.request();
  }
}
