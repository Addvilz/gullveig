import { Component, Input} from '@angular/core';

@Component({
  selector: 'app-json-view',
  template: `
    <div class="ngx-json-view">
      <json-view [data]="data" [level]="level" [levelOpen]="levelOpen" [root]="true" class="json-view"></json-view>
    </div>
  `
})
export class AppJsonViewComponent {
  @Input() data;
  @Input() levelOpen: number;

  key: string;
  level: number = 0;
}
