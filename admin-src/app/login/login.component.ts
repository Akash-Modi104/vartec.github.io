import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CmsApiService } from '../cms-api.service';

@Component({ selector: 'cms-login', templateUrl: './login.component.html' })
export class LoginComponent implements OnInit {
  loading = false;
  error = '';
  showPassword = false;
  readonly form = this.fb.group({ username: ['', Validators.required], password: ['', Validators.required] });

  constructor(private fb: FormBuilder, private api: CmsApiService, private router: Router) {}
  ngOnInit(): void { this.api.session(true).subscribe(session => { if (session.authenticated) this.router.navigate(['/']); }); }
  submit(): void {
    if (this.form.invalid || this.loading) { this.form.markAllAsTouched(); return; }
    this.loading = true;
    this.error = '';
    const username = this.form.value.username || '';
    const password = this.form.value.password || '';
    this.api.login(username, password).subscribe({
      next: () => this.router.navigate(['/']),
      error: error => { this.error = error.error?.detail || 'Sign in failed. Please try again.'; this.loading = false; }
    });
  }
}
