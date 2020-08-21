import { Pipe, PipeTransform } from '@angular/core';
import * as moment from 'moment'

@Pipe({name: 'f_ts_ago'})
export class TimeAgoPipe implements PipeTransform {
  transform(timestamp: number): string {
    return moment.utc(timestamp).fromNow();
  }
}
