import {Pipe, PipeTransform} from '@angular/core';

@Pipe({name: 'f_health_name'})
export class HealthNamePipe implements PipeTransform {
  transform(status: number): string {
    if (status === 0) {
      return 'Resolved';
    }
    if (status === 1) {
      return 'Incident';
    }
    if (status === 2) {
      return 'Critical';
    }
    if (status === 3) {
      return 'Unknown';
    }
  }
}
