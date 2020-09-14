import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MaterialModule} from '../material.module';
import {StatusViewComponent} from './views/status-view/status-view.component';
import {HttpClientModule} from '@angular/common/http';
import {PercentagePipe} from './pipes/Percentage.pipe';
import {TimeAgoPipe} from './pipes/TimeAgo.pipe';
import {StatusNamePipe} from './pipes/StatusName.pipe';
import {StatusClassPipe} from './pipes/StatusClass.pipe';
import {MetricsViewComponent} from './views/metrics-view/metrics-view.component';
import {MetaViewComponent} from './views/meta-view/meta-view.component';
import {ReactiveFormsModule} from '@angular/forms';
import {MetricsViewIndexComponent} from './views/metrics-view/metrics-view-index/metrics-view-index.component';
import {MetricsViewDashboardComponent} from './views/metrics-view/metrics-view-dashboard/metrics-view-dashboard.component';
import {MetaViewIndexComponent} from './views/meta-view/meta-view-index/meta-view-index.component';
import {MetaViewDashboardComponent} from './views/meta-view/meta-view-dashboard/meta-view-dashboard.component';
import {ChartComponent} from './components/chart/chart.component';
import {HealthViewComponent} from './views/health-view/health-view.component';
import {AboutViewComponent} from './views/about-view/about-view.component';
import {SignInViewComponent} from './views/sign-in-view/sign-in-view.component';
import {AuthGuard} from './auth.guard';
import {HealthNamePipe} from './pipes/HealthName.pipe';
import {HealthClassPipe} from './pipes/HealthClass.pipe';
import {NoDataComponent} from './components/no-data/no-data.component';
import {DataViewComponent} from './components/data-view/data-view.component';
import {NgVarDirective} from './directives/ng-var.directive';

@NgModule({
  declarations: [
    AppComponent,
    StatusViewComponent,
    PercentagePipe,
    TimeAgoPipe,
    StatusNamePipe,
    StatusClassPipe,
    HealthNamePipe,
    HealthClassPipe,
    MetricsViewComponent,
    MetaViewComponent,
    MetricsViewIndexComponent,
    MetricsViewDashboardComponent,
    MetaViewIndexComponent,
    MetaViewDashboardComponent,
    ChartComponent,
    HealthViewComponent,
    AboutViewComponent,
    SignInViewComponent,
    NoDataComponent,
    MetaViewComponent,
    DataViewComponent,
    NgVarDirective
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MaterialModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: [AuthGuard],
  bootstrap: [AppComponent]
})
export class AppModule {
}
