import {Injectable} from '@angular/core';
import {Subject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ViewUpdaterService {
  signal: Subject<Date> = new Subject<Date>();

  constructor() {
  }

  request(): void {
    this.signal.next(new Date());
  }
}
