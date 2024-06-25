import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeaturesProjectComponent } from './features-project.component';

describe('FeaturesProjectComponent', () => {
  let component: FeaturesProjectComponent;
  let fixture: ComponentFixture<FeaturesProjectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FeaturesProjectComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FeaturesProjectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
