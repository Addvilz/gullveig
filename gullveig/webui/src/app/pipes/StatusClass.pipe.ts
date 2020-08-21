import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'f_status_class'})
export class StatusClassPipe implements PipeTransform {
  transform(status: number): string {
    if (status === 0) {
      return 'service-status ok';
    }
    if (status === 1) {
      return 'service-status warning';
    }
    if (status === 2) {
      return 'service-status critical';
    }
    if (status === 3) {
      return 'service-status unknown';
    }
  }
}
