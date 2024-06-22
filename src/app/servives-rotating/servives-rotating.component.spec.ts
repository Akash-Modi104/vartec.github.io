import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServivesRotatingComponent } from './servives-rotating.component';

describe('ServivesRotatingComponent', () => {
  let component: ServivesRotatingComponent;
  let fixture: ComponentFixture<ServivesRotatingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServivesRotatingComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ServivesRotatingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
