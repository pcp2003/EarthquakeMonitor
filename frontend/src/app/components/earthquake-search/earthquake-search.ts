import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EarthquakeService } from '../../services/earthquake.service';
import { EarthquakeListResponse } from '../../api/model/earthquake-list-response';
import { EarthquakeFilter } from '../../api/model/earthquake-filter';
import { PaginationParams } from '../../api/model/pagination-params';
import { FilterFormComponent } from './filters/earthquake-filters';
import { ResultsTableComponent } from './results/earthquake-results';
import { finalize } from 'rxjs/operators';

/**
 * Orchestrator component for earthquake search functionality.
 * 
 * Manages state for filters, pagination, and API communication.
 * Orchestrates the display and interaction between filter form and results table.
 * 
 * Child components:
 * - FilterFormComponent: Search filters
 * - ResultsTableComponent: Search results with pagination
 */
@Component({
  selector: 'app-earthquake-search',
  standalone: true,
  imports: [CommonModule, FilterFormComponent, ResultsTableComponent],
  templateUrl: './earthquake-search.html',
  styleUrl: './earthquake-search.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})

export class EarthquakeSearchComponent {

  earthquakes = signal<EarthquakeListResponse | null>(null);
  error = signal<string | null>(null);
  pagination: PaginationParams = {
    page: 1,
    limit: 20,
  };
  filters: EarthquakeFilter = {};

  constructor(
    private earthquakeService: EarthquakeService,
  ) {}

  /**
   * Handles filter changes from the filters component.
   * Resets pagination to page 1 and loads earthquakes.
   */
  onFilterChange(filters: EarthquakeFilter): void {
    this.filters = filters;
    this.pagination.page = 1;
    this.loadEarthquakes();
  }

  /**
   * Handles load button click from the filters component.
   * Loads earthquakes with current filters without modifying them.
   */
  onLoadClick(): void {
    this.pagination.page = 1;
    this.loadEarthquakes();
  }

  /**
   * Resets all filters.
   * Only clears filter values without loading earthquakes.
   */
  onResetFilters(): void {
    this.filters = {};
  }

  /**
   * Handles page change from the results component.
   * Updates pagination and loads earthquakes for the new page.
   */
  onPageChange(page: number): void {
    if (page >= 1) {
      this.pagination.page = page;
      this.loadEarthquakes();
    }
  }

  /**
   * Loads earthquakes with current filters and pagination.
   */
  private loadEarthquakes(): void {
    this.error.set(null);

    this.earthquakeService.listEarthquakes(this.filters, this.pagination)
      .subscribe({
        next: (data) => {
          this.earthquakes.set(data);
        },
        error: (err) => {
          this.error.set(`Failed to load earthquakes: ${err.message || err.status || 'Unknown error'}`);
        },
      });
  }
}
