import { Component, OnInit } from '@angular/core';
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
})
export class EarthquakeList implements OnInit {
  earthquakes: EarthquakeListResponse | null = null;
  loading = true;
  error: string | null = null;

  // Default pagination
  pagination: PaginationParams = {
    page: 1,
    limit: 20,
  };

  // Default empty filters
  filters: EarthquakeFilter = {};

  constructor(private earthquakeService: EarthquakeService) {}

  ngOnInit(): void {
    this.loadEarthquakes();
  }

  /**
   * Load earthquakes with current filters and pagination.
   */
  loadEarthquakes(): void {
    this.loading = true;
    this.error = null;

    this.earthquakeService.listEarthquakes(this.filters, this.pagination).subscribe({
      next: (data) => {
        this.earthquakes = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching earthquakes:', err);
        this.error = 'Failed to load earthquakes. Please try again.';
        this.loading = false;
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
   * Apply filters and reset to first page.
   */
  applyFilters(newFilters: EarthquakeFilter): void {
    this.filters = newFilters;
    this.pagination.page = 1;
    this.loadEarthquakes();
  }
}
