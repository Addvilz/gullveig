import {Component, OnDestroy, OnInit} from '@angular/core';
import {LoaderIndicatorService} from '../../services/loader-indicator.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-no-data',
  templateUrl: './no-data.component.html',
  styleUrls: ['./no-data.component.scss']
})
export class NoDataComponent implements OnInit, OnDestroy {
  isLoading: boolean;
  private loaderSubscription: Subscription;

  constructor(private loader: LoaderIndicatorService) {
  }

  ngOnInit(): void {
    this.loaderSubscription = this.loader.isLoading.subscribe(it => {
      this.isLoading = it;
    });
  }

  ngOnDestroy(): void {
    this.loaderSubscription.unsubscribe()
  }

}
