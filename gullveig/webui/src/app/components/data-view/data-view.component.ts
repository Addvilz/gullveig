import {Component, Input} from '@angular/core';
import {isArray, isBoolean, isNumber, isObject, isString, isUndefined} from './utils';

@Component({
  selector: 'app-data-view',
  templateUrl: './data-view.component.html',
  styleUrls: ['./data-view.component.scss']
})
export class DataViewComponent {
  @Input() data: any;

  isSimple(data: any) {
    return isBoolean(data)
      || isString(data)
      || isNumber(data)
      || isUndefined(data)
      || null === data;
  }

  keysOf(data: any) {
    return Object.keys(data);
  }

  scalarClass(data: any) {
    if (false === data) {
      return 'false';
    }
    if (true === data) {
      return 'false';
    }
    if (null === data) {
      return 'false';
    }
    if (isNumber(data)) {
      return 'number';
    }
  }

  formatValue(data: any) {
    if (false === data) {
      return 'False';
    }
    if (true === data) {
      return 'True';
    }
    if (null === data) {
      return 'None';
    }
    return data;
  }

  isArray(data: any) {
    return isArray(data);
  }

  isObject(data: any) {
    return !isArray(data) && isObject(data);
  }
}
