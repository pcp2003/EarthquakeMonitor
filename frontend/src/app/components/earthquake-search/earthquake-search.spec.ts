import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EarthquakeSearchComponent } from './earthquake-search';

describe('EarthquakeSearchComponent', () => {
  let component: EarthquakeSearchComponent;
  let fixture: ComponentFixture<EarthquakeSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EarthquakeSearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EarthquakeSearchComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
