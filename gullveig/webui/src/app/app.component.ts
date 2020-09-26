import {Component} from '@angular/core';
import {ApiClientService, VersionsResponse} from './services/api-client.service';
import {Router} from '@angular/router';
import {ViewUpdaterService} from './services/view-updater.service';
import {LoaderIndicatorService} from './services/loader-indicator.service';
import {MatSnackBar} from '@angular/material/snack-bar';

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
    public loader: LoaderIndicatorService,
    private snackbar: MatSnackBar
  ) {
    api.isKnownUser.subscribe(it => {
      this.isKnownUser = it;

      if (this.isKnownUser) {
        this.verifyWebServerCompat();
      }
    });
  }

  signOut() {
    this.api.setToken(null);
    this.router.navigate(['/sign-in/']);
  }

  emitUpdateView() {
    this.viewUpdater.request();
  }

  private alertWebServerMismatch() {
    this.snackbar.open(
      'Web UI version differs from reporting server version. ' +
      'Update and restart the web UI server, then reload this page to apply the update. ',
      'Acknowledge',
      {
        duration: 15000,
        panelClass: 'error-alert',
        verticalPosition: 'top'
      }
    );
  }

  private verifyWebServerCompat() {
    this.api.fetchVersions().subscribe(iit => {
      if (iit.server !== iit.web) {
        this.alertWebServerMismatch();
      }
    });
  }
}
