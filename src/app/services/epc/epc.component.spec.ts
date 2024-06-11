import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EpcComponent } from './epc.component';

describe('EpcComponent', () => {
  let component: EpcComponent;
  let fixture: ComponentFixture<EpcComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EpcComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EpcComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
