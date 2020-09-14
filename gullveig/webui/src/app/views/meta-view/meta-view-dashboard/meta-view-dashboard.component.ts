import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ApiClientService, MetaRecord, MetaResponse} from '../../../services/api-client.service';
import {BehaviorSubject, Subscription} from 'rxjs';
import {ViewUpdaterService} from '../../../services/view-updater.service';

@Component({
    selector: 'app-meta-view-dashboard',
    templateUrl: './meta-view-dashboard.component.html',
    styleUrls: ['./meta-view-dashboard.component.scss']
})
export class MetaViewDashboardComponent implements OnDestroy, OnInit {
    ident: BehaviorSubject<string> = new BehaviorSubject<string>(null);
    selected: BehaviorSubject<MetaRecord> = new BehaviorSubject<MetaRecord>(null);
    metas: MetaResponse;
    @ViewChild('right') right;
    private viewUpdateSubscription: Subscription;

    constructor(private route: ActivatedRoute, private api: ApiClientService, private viewUpdater: ViewUpdaterService) {
        this.ident.subscribe(it => {
            this.loadData(it);
        });

        this.route.params.subscribe(it => {
            this.ident.next(it.ident);
        });
    }

    select(record: MetaRecord) {
        this.selected.next(record);
        if (this.right) {
            this.right.nativeElement.scrollTo(0, 0);
        }
    }

    ngOnInit(): void {
        this.viewUpdateSubscription = this.viewUpdater.signal.subscribe(_ => {
            this.loadData(this.ident.value);
        });
    }

    ngOnDestroy() {
        this.viewUpdateSubscription.unsubscribe();
    }

    private loadData(ident: string) {
        if (!ident) {
            return;
        }
        this.api.fetchMeta(ident).subscribe(it => {
            this.metas = it;
            if (this.selected.value === null) {
                // TODO meh...
                setTimeout(() => this.selected.next(this.metas[0]), 50);
            }
        });
    }
}
