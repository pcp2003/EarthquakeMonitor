import { TestBed } from '@angular/core/testing';

import { Earthquake } from './earthquake';

describe('Earthquake', () => {
  let service: Earthquake;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Earthquake);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
