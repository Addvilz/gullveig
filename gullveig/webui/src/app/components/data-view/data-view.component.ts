import {Component, Input} from '@angular/core';
import {formatValue, isArray, isNumber, isObject, isSimple} from './utils';

interface DataTableProjection {
  cols: string[];
  rows: object[];
}

@Component({
  selector: 'app-data-view',
  templateUrl: './data-view.component.html',
  styleUrls: ['./data-view.component.scss']
})
export class DataViewComponent {
  @Input() data: any;

  isTabular(data: any) {
    if (isArray(data)) {
      for (const item of data) {
        if (isSimple(item)) {
          return false;
        }

        if (!isObject(item)) {
          return false;
        }

        for (const nestedValue of Object.values(item)) {
          if (!isSimple(nestedValue)) {
            return false;
          }
        }
      }
      return true;
    }

    if (isObject(data)) {
      for (const item of Object.values(data)) {
        if (isSimple(item)) {
          return false;
        }

        if (!isObject(item)) {
          return false;
        }

        for (const nestedValue of Object.values(item)) {
          if (!isSimple(nestedValue)) {
            return false;
          }
        }
      }
      return true;
    }

    return false;
  }

  projectTable(data): DataTableProjection {
    const table = {
      cols: [],
      rows: []
    };

    if (isArray(data)) {
      let index = 1;
      for (const record of data) {
        for (const key in record) {
          if (!record.hasOwnProperty(key)) {
            continue;
          }

          if (table.cols.indexOf(key) === -1) {
            table.cols.push(key);
          }
        }
        const clone = JSON.parse(JSON.stringify(record));
        clone.__idx = index;
        table.rows.push(clone);
        index++;
      }

      return table;
    }


    for (const index in data) {
      if (!data.hasOwnProperty(index)) {
        continue;
      }

      const record = data[index];

      for (const key in record) {
        if (!record.hasOwnProperty(key)) {
          continue;
        }

        if (table.cols.indexOf(key) === -1) {
          table.cols.push(key);
        }
      }
      const clone = JSON.parse(JSON.stringify(record));
      clone.__idx = index;
      table.rows.push(clone);
    }

    return table;
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

  isSimple(data: any) {
    return isSimple(data);
  }

  formatValue(data: any) {
    return formatValue(data);
  }

  isArray(data: any) {
    return isArray(data);
  }

  isObject(data: any) {
    return !isArray(data) && isObject(data);
  }

  safeGet(row: object, col: string) {
    if (row.hasOwnProperty(col)) {
      return row[col];
    }
    return null;
  }

  deduplicate(data: any[]) {
    return data.filter((v, i, s) => {
      return s.indexOf(v) === i;
    });
  }

  isArrayList(data: any) {
    if (!Array.isArray(data)) {
      return false;
    }

    for (const entry of data) {
      if (!isSimple(entry)) {
        return false;
      }
    }
    return true;
  }
}
