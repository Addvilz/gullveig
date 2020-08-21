import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ApiClientService, HealthResponse, HealthResponseItem} from '../../services/api-client.service';
import {Subscription} from 'rxjs';
import {ViewUpdaterService} from '../../services/view-updater.service';
import {FormControl} from '@angular/forms';

@Component({
  selector: 'app-health-view',
  templateUrl: './health-view.component.html',
  styleUrls: ['./health-view.component.scss']
})
export class HealthViewComponent implements OnInit, OnDestroy {
  idents = new FormControl();
  @ViewChild('stateFilter') stateFilter;

  identList: string[] = [];
  health: HealthResponse;
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

  // Sigh...
  filteredHealthRecords() {
    if (!this.health) {
      return [];
    }
    return (this.health as Array<HealthResponseItem>).filter(it => {

      if (this.stateFilter?.value?.length > 0) {
        if (-1 === this.stateFilter.value.indexOf(it.status)) {
          return false;
        }
      }

      if (!!this.idents.value && this.idents.value.length > 0) {
        if (-1 === this.idents.value.indexOf(it.ident)) {
          return false;
        }
      }

      return true;
    });
  }

  private loadData() {
    this.api.fetchHealth().subscribe(it => {
      const idents = [];
      for (const record of it) {
        idents.push(record.ident);
      }
      this.health = it;
      this.identList = idents.filter((v, i, s) => s.indexOf(v) === i);
    });
  }
}
