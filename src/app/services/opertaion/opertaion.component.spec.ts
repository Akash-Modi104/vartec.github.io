import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OpertaionComponent } from './opertaion.component';

describe('OpertaionComponent', () => {
  let component: OpertaionComponent;
  let fixture: ComponentFixture<OpertaionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OpertaionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OpertaionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
