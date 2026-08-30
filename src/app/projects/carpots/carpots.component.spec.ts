import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { CarpotsComponent } from './carpots.component';

describe('CarpotsComponent', () => {
  let component: CarpotsComponent;
  let fixture: ComponentFixture<CarpotsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranslateModule.forRoot()],
      declarations: [ CarpotsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CarpotsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
