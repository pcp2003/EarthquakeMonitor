import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EarthquakeList } from './earthquake-list';

describe('EarthquakeList', () => {
  let component: EarthquakeList;
  let fixture: ComponentFixture<EarthquakeList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EarthquakeList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EarthquakeList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
