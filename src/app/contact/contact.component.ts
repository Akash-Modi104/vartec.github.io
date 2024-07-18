import { Component, OnInit, OnDestroy } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from 'src/app/language.service';
import { ConfigService } from 'src/app/config.service';
import { Subscription } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit, OnDestroy {
  contactForm!: FormGroup; // Use the non-null assertion operator
  languageChangeSubscription: Subscription;

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private configService: ConfigService,
    private http: HttpClient,
    private fb: FormBuilder,
    private toastr: ToastrService
  ) {
    this.languageChangeSubscription = this.translate.onLangChange.subscribe(() => {
      console.log('language changed');
    });
  }

  ngOnInit(): void {
    this.contactForm = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', Validators.required],
      message: ['', Validators.required]
    });
  }

  ngOnDestroy(): void {
    this.languageChangeSubscription.unsubscribe();
  }

  sendEmail(): void {
    this.toastr.success('Thanks for conatcting us. will back to you shortly', 'Success');
    if (this.contactForm.valid) {
      const headers = new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' });
      const body = new URLSearchParams(this.contactForm.value).toString();

      this.http.post('send_mail.php', body, { headers, responseType: 'text' }).subscribe(
        response => {
          this.toastr.success('Thanks for conatcting us. will back to you shortly', 'Success');
          this.contactForm.reset();
        },
        error => {
          this.toastr.error('An error occurred while sending email. Please try again.', 'Error');
        }
      );
    } else {
      this.toastr.error('Please fill in all required fields.', 'Error');
    }
  }
}
