import {AfterViewChecked, AfterViewInit, Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import * as MarkdownIt from 'markdown-it';
import * as Token from 'markdown-it/lib/token';
import MarkdownItAnchor from 'markdown-it-anchor';
import slugify from 'slugify';
import {ActivatedRoute, Router} from '@angular/router';
import * as hljs from './hljs'

const slugifyOptions = {
  lower: true,
  strict: true,
}

@Component({
  selector: 'app-markdown',
  templateUrl: './markdown.component.html',
  styleUrls: ['./markdown.component.scss']
})
export class MarkdownComponent implements OnInit, OnChanges, AfterViewInit, AfterViewChecked {
  @Input() basePath: string;
  @Input() markdown: string;
  @ViewChild('markdownWrapper') htmlContainerWrapper;
  @ViewChild('markdown') htmlContainer;

  html: string;
  nav: any[];
  private md: MarkdownIt;
  private navigateTo: string;

  constructor(private router: Router, private activatedRoute: ActivatedRoute) {
    this.md = new MarkdownIt({
      html: true,
      linkify: false,
      highlight: (str, lang) => {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(lang, str).value;
          } catch (__) {
          }
        }
        return '';
      }
    });

    this.md.use(MarkdownItAnchor, {
      permalink: true,
      permalinkBefore: true,
      permalinkSymbol: 'link',
      permalinkHref: slug => {
        return document.location.pathname + '#' + slug;
      },
      slugify: text => slugify(text, slugifyOptions)
    });

    this.activatedRoute.fragment.subscribe(it => {
      if (!it) {
        this.navigateTo = undefined;
        return;
      }

      this.navigateTo = decodeURIComponent(it);
    });
  }

  ngAfterViewInit(): void {
    this.attachNavigation();
  }

  ngAfterViewChecked(): void {
    this.attachNavigation();
  }

  ngOnInit(): void {
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes.markdown) {
      return;
    }

    let tokens = this.md.parse(changes.markdown.currentValue, {});
    this.html = this.md.renderer.render(tokens, this.md.options, {});
    this.nav = this.constructNav(tokens);
  }

  goTo(item: any) {
    this.router.navigate([], {fragment: item.slug});
  }

  private constructNav(tokens: Token[]) {
    const nav = [];
    let i = 0;
    for (const token of tokens) {
      const nt = tokens[i + 1];
      i++;

      if (token.type === 'heading_open') {
        if (token.tag === 'h2' && nt && nt.type === 'inline') {
          nav.push({
            'name': nt.content,
            'slug': slugify(nt.content, slugifyOptions),
            'children': []
          });
        } else if (token.tag === 'h3' && nav.length > 0 && nt && nt.type === 'inline') {
          nav[nav.length - 1].children.push({
            'name': nt.content,
            'slug': slugify(nt.content, slugifyOptions),
          });
        }
      }
    }

    return nav;
  }

  private attachNavigation() {
    this.htmlContainer.nativeElement.querySelectorAll('a').forEach(link => {

      if (link.className === 'header-anchor' && -1 !== link.href.indexOf('#')) {
        link.parentNode.id = decodeURIComponent(link.href.substring(1 + link.href.indexOf('#')));
      }

      if (link.getAttribute('href').startsWith(this.basePath)
        && !link.hasAttribute('ng-nav-attached')) {
        link.setAttribute('ng-nav-attached', 'yes');
        let href = new URL(link.href);

        const routerPath = ['/kb/article/'].concat(href.pathname.substring(12).split('/'));
        let fragment = undefined;
        if (href.hash) {
          fragment = href.hash.substring(1);
        }

        link.addEventListener('click', e => {
          // NOTE: query params are explicitly ignored here, since articles have no use for them
          this.router.navigate(routerPath, {fragment});
          e.preventDefault();
        });
      }
    });

    if (this.navigateTo) {
      const target = this.htmlContainer.nativeElement.querySelector('#' + CSS.escape(this.navigateTo));

      if (target) {
        target.scrollIntoView();
      }
    } else {
      this.htmlContainerWrapper.nativeElement.scrollTo(0, 0);
    }
  }
}
