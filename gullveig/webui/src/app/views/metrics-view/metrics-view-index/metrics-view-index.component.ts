import {Component, OnDestroy, OnInit} from '@angular/core';
import {ApiClientService, IdentListResponse} from '../../../services/api-client.service';
import {ViewUpdaterService} from '../../../services/view-updater.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-metrics-view-index',
  templateUrl: './metrics-view-index.component.html',
  styleUrls: ['./metrics-view-index.component.scss']
})
export class MetricsViewIndexComponent implements OnInit, OnDestroy {
  idents: IdentListResponse;
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
    this.api.fetchIdents().subscribe(it => {
      this.idents = it;
    });
  }
}
