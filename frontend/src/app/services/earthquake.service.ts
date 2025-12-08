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
   *
   * Sends filters and pagination parameters as a JSON request body.
   * This approach ensures proper OpenAPI schema generation and automatic
   * TypeScript interface generation from the backend specification.
   *
   * @param filters Filter parameters with validation (min/max magnitude, depth, time range, location, magnitude type)
   * @param pagination Pagination parameters with validation (page >= 1, limit 1-1000)
   * @returns Observable with the paginated response
   */
  listEarthquakes(
    filters?: EarthquakeFilter,
    pagination?: PaginationParams
  ): Observable<EarthquakeListResponse> {
    const request = {
      filters: filters || {},
      pagination: pagination || { page: 1, limit: 50 }
    };

    return this.http.post<EarthquakeListResponse>(
      `${this.apiUrl}/list`,
      request
    );
  }

  /**
   * Gets the details of a specific earthquake.
   *
   * @param id Unique earthquake identifier
   * @returns Observable with earthquake details
   */
  getEarthquakeDetails(id: string): Observable<EarthquakeResponse> {
    return this.http.get<EarthquakeResponse>(`${this.apiUrl}/${id}/details`);
  }

  /**
   * Triggers a manual synchronization of earthquake data from USGS API.
   *
   * @param request Optional synchronization request with since_datetime
   * @returns Observable with synchronization result
   */
  manualSync(request?: DataRequest): Observable<DataResponse> {
    return this.http.post<DataResponse>(`${this.apiUrl}/ManualSync`, request || {});
  }

  /**
   * Deletes all earthquake records from the database.
   * Useful for resetting the dataset during testing or maintenance.
   *
   * @returns Observable with deletion result message
   */
  deleteAllEarthquakes(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/delete_all`);
  }
}
