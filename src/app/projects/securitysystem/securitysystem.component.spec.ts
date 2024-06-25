import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecuritysystemComponent } from './securitysystem.component';

describe('SecuritysystemComponent', () => {
  let component: SecuritysystemComponent;
  let fixture: ComponentFixture<SecuritysystemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecuritysystemComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SecuritysystemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
