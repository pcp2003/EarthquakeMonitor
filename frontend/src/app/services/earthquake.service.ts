import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EarthquakeListResponse } from '../api/model/earthquake-list-response';
import { EarthquakeResponse } from '../api/model/earthquake-response';
import { DataResponse } from '../api/model/data-response';
import { DataRequest } from '../api/model/data-request';
import { EarthquakeFilter } from '../api/model/earthquake-filter';
import { PaginationParams } from '../api/model/pagination-params';

@Injectable({
  providedIn: 'root',
})
export class EarthquakeService {
  private readonly apiUrl = '/api/v1/earthquakes';

  constructor(private http: HttpClient) {}

  /**
   * Gets a paginated list of earthquakes with optional filtering.
   * @returns Observable with the paginated response
   */
  listEarthquakes(
    filters?: EarthquakeFilter,
    pagination?: PaginationParams
  ): Observable<EarthquakeListResponse> {
    // Remove undefined values to avoid sending empty fields
    const cleanedFilters = filters ? Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v !== undefined)
    ) : {};

    const request = {
      filters: cleanedFilters,
      pagination: pagination || { page: 1, limit: 50 }
    };

    return this.http.post<EarthquakeListResponse>(
      `${this.apiUrl}/list`,
      request
    );
  }
  
}
