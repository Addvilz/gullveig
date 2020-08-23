import { Component, OnInit } from '@angular/core';
import {ApiClientService, VersionsResponse} from '../../services/api-client.service';

@Component({
  selector: 'app-about-view',
  templateUrl: './about-view.component.html',
  styleUrls: ['./about-view.component.scss']
})
export class AboutViewComponent {
  versions: VersionsResponse;

  constructor(private api: ApiClientService) {
    this.api.fetchVersions().subscribe(it => {
      this.versions = it;
    })
  }
}
