import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'f_health_class'})
export class HealthClassPipe implements PipeTransform {
  transform(status: number): string {
    if (status === 0) {
      return 'health-status ok';
    }
    if (status === 1) {
      return 'health-status warning';
    }
    if (status === 2) {
      return 'health-status critical';
    }
    if (status === 3) {
      return 'health-status unknown';
    }
  }
}
