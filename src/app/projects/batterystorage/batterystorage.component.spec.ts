import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { BatterystorageComponent } from './batterystorage.component';

describe('BatterystorageComponent', () => {
  let component: BatterystorageComponent;
  let fixture: ComponentFixture<BatterystorageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranslateModule.forRoot()],
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
