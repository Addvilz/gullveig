import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'f_status_name'})
export class StatusNamePipe implements PipeTransform {
  transform(status: number): string {
    if (status === 0) {
      return 'Ok';
    }
    if (status === 1) {
      return 'Warning';
    }
    if (status === 2) {
      return 'Critical';
    }
    if (status === 3) {
      return 'Unknown';
    }
  }
}
