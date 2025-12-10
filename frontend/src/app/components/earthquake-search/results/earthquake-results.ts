import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EarthquakeListResponse } from '../../../api/model/earthquake-list-response';
import { PaginationControlComponent } from '../pagination/earthquake-pagination';
import './earthquake-results.css';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [CommonModule, PaginationControlComponent],
  templateUrl: './earthquake-results.html',
  styleUrl: './earthquake-results.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResultsTableComponent {
  earthquakes = input<EarthquakeListResponse | null>(null);
  error = input<string | null>(null);
  pageChange = output<number>();

  onPageChange(page: number): void {
    this.pageChange.emit(page);
  }
}
