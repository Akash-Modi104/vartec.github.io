import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FloatingsolarComponent } from './floatingsolar.component';

describe('FloatingsolarComponent', () => {
  let component: FloatingsolarComponent;
  let fixture: ComponentFixture<FloatingsolarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FloatingsolarComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FloatingsolarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
