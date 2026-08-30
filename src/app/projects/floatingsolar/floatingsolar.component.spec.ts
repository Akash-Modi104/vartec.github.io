import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { FloatingsolarComponent } from './floatingsolar.component';

describe('FloatingsolarComponent', () => {
  let component: FloatingsolarComponent;
  let fixture: ComponentFixture<FloatingsolarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranslateModule.forRoot()],
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
