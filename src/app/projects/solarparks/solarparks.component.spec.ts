import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SolarparksComponent } from './solarparks.component';

describe('SolarparksComponent', () => {
  let component: SolarparksComponent;
  let fixture: ComponentFixture<SolarparksComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SolarparksComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SolarparksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
