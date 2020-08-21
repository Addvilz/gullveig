import {Component, OnDestroy, OnInit} from '@angular/core';
import {ApiClientService, StatusResponse} from '../../services/api-client.service';
import {ViewUpdaterService} from '../../services/view-updater.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-status-view',
  templateUrl: './status-view.component.html',
  styleUrls: ['./status-view.component.scss']
})
export class StatusViewComponent implements OnInit, OnDestroy {
  status: StatusResponse;
  private viewUpdateSubscription: Subscription;

  constructor(private api: ApiClientService, private viewUpdater: ViewUpdaterService) {
    this.loadData();
  }

  ngOnInit(): void {
    this.viewUpdateSubscription = this.viewUpdater.signal.subscribe(_ => {
      this.loadData();
    });
  }

  ngOnDestroy() {
    this.viewUpdateSubscription.unsubscribe();
  }

  private loadData() {
    this.api.fetchStatus().subscribe(it => this.status = it);
  }
}
