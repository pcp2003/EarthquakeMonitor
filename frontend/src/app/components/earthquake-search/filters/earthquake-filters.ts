import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EarthquakeFilter } from '../../../api/model/earthquake-filter';
import './earthquake-filters.css';

@Component({
  selector: 'app-filter-form',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './earthquake-filters.html',
  styleUrl: './earthquake-filters.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilterFormComponent {
  @Input() filters: EarthquakeFilter = {};
  @Output() filterChange = new EventEmitter<EarthquakeFilter>();
  @Output() loadClick = new EventEmitter<void>();
  @Output() resetFilters = new EventEmitter<void>();

  onMinMagnitudeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      min_magnitude: value ? parseFloat(value) : undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onMaxMagnitudeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      max_magnitude: value ? parseFloat(value) : undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onMinDepthChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      min_depth: value ? parseFloat(value) : undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onMaxDepthChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      max_depth: value ? parseFloat(value) : undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onLocationChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      place_contains: value || undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onMagnitudeTypeChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    const updatedFilters = {
      ...this.filters,
      magnitude_type: value || undefined,
    };
    this.filterChange.emit(updatedFilters);
  }

  onLoadClick(): void {
    this.loadClick.emit();
  }

  onClearClick(): void {
    this.resetFilters.emit();
  }
}
