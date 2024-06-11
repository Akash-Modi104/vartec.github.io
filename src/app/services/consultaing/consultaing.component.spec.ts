import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConsultaingComponent } from './consultaing.component';

describe('ConsultaingComponent', () => {
  let component: ConsultaingComponent;
  let fixture: ComponentFixture<ConsultaingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ConsultaingComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConsultaingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
