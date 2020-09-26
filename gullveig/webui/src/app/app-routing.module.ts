import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {StatusViewComponent} from './views/status-view/status-view.component';
import {MetricsViewComponent} from './views/metrics-view/metrics-view.component';
import {MetaViewComponent} from './views/meta-view/meta-view.component';
import {MetricsViewIndexComponent} from './views/metrics-view/metrics-view-index/metrics-view-index.component';
import {MetricsViewDashboardComponent} from './views/metrics-view/metrics-view-dashboard/metrics-view-dashboard.component';
import {MetaViewIndexComponent} from './views/meta-view/meta-view-index/meta-view-index.component';
import {MetaViewDashboardComponent} from './views/meta-view/meta-view-dashboard/meta-view-dashboard.component';
import {HealthViewComponent} from './views/health-view/health-view.component';
import {AboutViewComponent} from './views/about-view/about-view.component';
import {SignInViewComponent} from './views/sign-in-view/sign-in-view.component';
import {AuthGuard} from './auth.guard';
import {KbViewComponent} from './views/kb-view/kb-view.component';

const routes: Routes = [
  {path: '', redirectTo: 'status', pathMatch: 'full'},
  {path: 'status', component: StatusViewComponent, canActivate: [AuthGuard]},
  {path: 'health', component: HealthViewComponent, canActivate: [AuthGuard]},
  {
    path: 'metrics', component: MetricsViewComponent, canActivate: [AuthGuard],
    children: [
      {path: '', component: MetricsViewIndexComponent},
      {path: ':ident', component: MetricsViewDashboardComponent},
      {path: ':ident/:mhash', component: MetricsViewDashboardComponent}
    ]
  },
  {
    path: 'meta', component: MetaViewComponent, canActivate: [AuthGuard],
    children: [
      {path: '', component: MetaViewIndexComponent},
      {path: ':ident', component: MetaViewDashboardComponent}
    ]
  },
  {path: 'about', component: AboutViewComponent},
  {
    path: 'kb', component: KbViewComponent, canActivate: [AuthGuard],
    children: [
      {path: '**', component: KbViewComponent}
    ]
  },
  {path: 'sign-in', component: SignInViewComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
