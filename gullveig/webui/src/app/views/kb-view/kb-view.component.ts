import {Component, OnInit} from '@angular/core';
import {ApiClientService, KBArticle, KBNavItem, KBNavView} from '../../services/api-client.service';
import {NavigationEnd, Router} from '@angular/router';
import {ViewUpdaterService} from '../../services/view-updater.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-kb-view',
  templateUrl: './kb-view.component.html',
  styleUrls: ['./kb-view.component.scss']
})
export class KbViewComponent implements OnInit {
  navigation: KBNavView;
  articleUri: string;
  defaultUri: string;
  loadedUri: string;
  article: KBArticle;
  isFetching: Boolean;
  private viewUpdateSubscription: Subscription;
  private routerSubscription: Subscription;

  constructor(private api: ApiClientService, private router: Router, private viewUpdater: ViewUpdaterService) {
    this.routerSubscription = router.events.subscribe(it => {
      if (!(it instanceof NavigationEnd)) {
        return;
      }

      let targetArticleUri = it.urlAfterRedirects;

      if (-1 !== targetArticleUri.indexOf('#')) {
        targetArticleUri = targetArticleUri.substring(0, targetArticleUri.indexOf('#'));
      }

      if (targetArticleUri.startsWith('/kb/article/')) {
        targetArticleUri = targetArticleUri.substr(12);
      } else {
        targetArticleUri = '';
      }

      if (targetArticleUri === this.articleUri) {
        return;
      }

      this.articleUri = targetArticleUri;
      this.fetch();
    });

    this.isFetching = true;
    this.fetchNavigation(() => this.isFetching = false);
  }

  ngOnInit(): void {
    this.fetch();

    this.viewUpdateSubscription = this.viewUpdater.signal.subscribe(_ => {
      this.fetchNavigation(() => {
        this.fetch(true);
      });
    });
  }

  ngOnDestroy() {
    this.viewUpdateSubscription.unsubscribe();
    this.routerSubscription.unsubscribe();
  }

  goTo(item: KBNavItem): void {
    if (item.uri === this.defaultUri) {
      this.router.navigate(['/kb/']);
      return;
    }
    this.router.navigate(['/kb/article/'].concat(item.uri.split('/')));
  }

  hasContent() {
    return !!this.navigation && (!!this.navigation.default || !!this.navigation.categories) &&
      (this.navigation.default.items.length > 0
        || this.navigation.categories.length > 0);
  }

  private fetch(force: boolean = false): void {
    let target;

    if (this.articleUri) {
      target = this.articleUri;
    } else if (!!this.defaultUri) {
      target = this.defaultUri;
    } else {
      target = undefined;
    }

    if (target && (target !== this.loadedUri || force)) {
      this.fetchArticle(target);
      this.loadedUri = target;
    }
  }

  private fetchArticle(article: string): void {
    this.api.fetchKBArticle(article).subscribe(it => {
      this.article = it;
    });
  }

  private defaultIndex(): string | undefined {
    if (!this.navigation || !this.navigation.default) {
      return undefined;
    }

    for (const item of this.navigation.default.items) {
      if (item.uri.toLowerCase() === 'readme' || item.uri.toLowerCase() === 'index') {
        return item.uri;
      }
    }

    if (this.navigation.default.items.length > 0) {
      return this.navigation.default.items[0].uri;
    }

    return undefined;
  }

  private fetchNavigation(done: () => void | null) {
    this.api.fetchKbNavigation().subscribe(it => {
      this.navigation = it;
      this.defaultUri = this.defaultIndex();
      this.fetch();
      if (done) {
        done();
      }
    });
  }
}
