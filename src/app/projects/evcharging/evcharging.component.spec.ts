import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { EvchargingComponent } from './evcharging.component';

describe('EvchargingComponent', () => {
  let component: EvchargingComponent;
  let fixture: ComponentFixture<EvchargingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranslateModule.forRoot()],
      declarations: [ EvchargingComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EvchargingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
