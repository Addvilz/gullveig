import {Component} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {ApiClientService} from '../../services/api-client.service';

@Component({
  selector: 'app-sign-in-view',
  templateUrl: './sign-in-view.component.html',
  styleUrls: ['./sign-in-view.component.scss']
})
export class SignInViewComponent {
  signInForm = new FormGroup({
    username: new FormControl('', [
      Validators.required
    ]),
    password: new FormControl('', [
      Validators.required
    ]),
  });

  username = this.signInForm.get('username');
  password = this.signInForm.get('password');
  isLoading = false;

  constructor(private router: Router, private api: ApiClientService) {
  }

  onSubmit() {
    this.api
      .signIn(this.signInForm.value)
      .subscribe(it => {
        this.api.setToken(it.token);
        this.router.navigate(['/']);
      });
  }
}
