import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
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
  earthquakes: EarthquakeListResponse | null = null;
  loading = false;
  error: string | null = null;

  // Default pagination
  pagination: PaginationParams = {
    page: 1,
    limit: 20,
  };

  // Default empty filters
  filters: EarthquakeFilter = {};

  constructor(
    private earthquakeService: EarthquakeService,
    private cdr: ChangeDetectorRef
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
    this.cdr.markForCheck();
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
   * Sets loading to false and triggers change detection when complete.
   */
  private loadEarthquakes(): void {
    this.loading = true;
    this.error = null;
    this.cdr.markForCheck();

    this.earthquakeService.listEarthquakes(this.filters, this.pagination)
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe({
        next: (data) => {
          this.earthquakes = data;
        },
        error: (err) => {
          this.error = `Failed to load earthquakes: ${err.message || err.status || 'Unknown error'}`;
        },
      });
  }
}
