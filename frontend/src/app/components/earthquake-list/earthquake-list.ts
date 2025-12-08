import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EarthquakeService } from '../../services/earthquake.service';
import { EarthquakeListResponse } from '../../api/model/earthquake-list-response';
import { EarthquakeFilter } from '../../api/model/earthquake-filter';
import { PaginationParams } from '../../api/model/pagination-params';

@Component({
  selector: 'app-earthquake-list',
  imports: [CommonModule],
  templateUrl: './earthquake-list.html',
  styleUrl: './earthquake-list.css',
  changeDetection: ChangeDetectionStrategy.Default,
})

export class EarthquakeList {
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

  constructor(private earthquakeService: EarthquakeService, private cdr: ChangeDetectorRef) {}

  /**
   * Load earthquakes with current filters and pagination.
   */
  loadEarthquakes(): void {
    this.loading = true;
    this.error = null;
    this.cdr.markForCheck();

    console.log('Loading earthquakes with filters:', this.filters, 'and pagination:', this.pagination);

    this.earthquakeService.listEarthquakes(this.filters, this.pagination).subscribe({
      next: (data) => {
        console.log('Successfully loaded earthquakes:', data);
        this.earthquakes = data;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error fetching earthquakes:', err);
        this.error = `Failed to load earthquakes: ${err.message || err.status || 'Unknown error'}`;
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  /**
   * Go to a specific page.
   */
  goToPage(page: number): void {
    if (page >= 1) {
      this.pagination.page = page;
      this.loadEarthquakes();
    }
  }

  /**
   * Update minimum magnitude filter
   */
  onMinMagnitudeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.min_magnitude = value ? parseFloat(value) : undefined;
    this.pagination.page = 1;
  }

  /**
   * Update maximum magnitude filter
   */
  onMaxMagnitudeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.max_magnitude = value ? parseFloat(value) : undefined;
    this.pagination.page = 1;
  }

  /**
   * Update minimum depth filter
   */
  onMinDepthChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.min_depth = value ? parseFloat(value) : undefined;
    this.pagination.page = 1;
  }

  /**
   * Update maximum depth filter
   */
  onMaxDepthChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.max_depth = value ? parseFloat(value) : undefined;
    this.pagination.page = 1;
  }

  /**
   * Update location filter
   */
  onLocationChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.place_contains = value || undefined;
    this.pagination.page = 1;
  }

  /**
   * Update magnitude type filter
   */
  onMagnitudeTypeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filters.magnitude_type = value || undefined;
    this.pagination.page = 1;
  }

  /**
   * Clear all filters and reset to first page
   */
  clearFilters(): void {
    this.filters = {};
    this.pagination.page = 1;
  }

}
