import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoaderIndicatorService {
  isLoading: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  private numProcesses = 0;

  inc(): void {
    ++this.numProcesses;
    this.isLoading.next(true);
  }

  dec(): void {
    if (0 < this.numProcesses) {
      --this.numProcesses;
    }
    this.isLoading.next(0 < this.numProcesses);
  }
}
