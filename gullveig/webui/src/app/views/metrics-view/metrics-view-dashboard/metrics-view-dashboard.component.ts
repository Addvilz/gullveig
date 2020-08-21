import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {BehaviorSubject, Subscription} from 'rxjs';
import {ApiClientService, MetricsResponse} from '../../../services/api-client.service';
import {ViewUpdaterService} from '../../../services/view-updater.service';

@Component({
  selector: 'app-metrics-view-dashboard',
  templateUrl: './metrics-view-dashboard.component.html',
  styleUrls: ['./metrics-view-dashboard.component.scss']
})
export class MetricsViewDashboardComponent implements OnInit, OnDestroy {
  @ViewChild('records') recordsList;
  metrics: MetricsResponse;
  ident: BehaviorSubject<string> = new BehaviorSubject<string>(null);
  selected: string;
  period: BehaviorSubject<string> = new BehaviorSubject<string>('min');
  private viewUpdateSubscription: Subscription;

  constructor(
    private route: ActivatedRoute,
    private api: ApiClientService,
    private viewUpdater: ViewUpdaterService
  ) {
    this.ident.subscribe(it => {
      this.loadData(it, this.period.value);
    });

    this.period.subscribe(it => {
      this.loadData(this.ident.value, it);
    });

    this.route.params.subscribe(it => {
      this.ident.next(it.ident);
      if (it.mhash) {
        this.selected = it.mhash;
      }
    });
  }

  select(metric: string) {
    this.selected = metric;
  }

  ngOnInit(): void {
    this.viewUpdateSubscription = this.viewUpdater.signal.subscribe(_ => {
      this.loadData(this.ident.value, this.period.value);
    });
  }

  ngOnDestroy() {
    this.viewUpdateSubscription.unsubscribe();
  }

  private loadData(ident: string, period: string): void {
    if (!ident) {
      return;
    }

    this.api.fetchMetrics(ident, period).subscribe(it => {
      this.metrics = it;
    });
  }
}
