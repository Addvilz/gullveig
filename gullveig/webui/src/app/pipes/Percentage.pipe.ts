import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'f_percent'})
export class PercentagePipe implements PipeTransform {
  transform(value: number): string {
    return value.toFixed(2) + '%';
  }
}
