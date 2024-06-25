import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BatterystorageComponent } from './batterystorage.component';

describe('BatterystorageComponent', () => {
  let component: BatterystorageComponent;
  let fixture: ComponentFixture<BatterystorageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BatterystorageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BatterystorageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
