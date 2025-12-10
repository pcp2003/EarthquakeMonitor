import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
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
  @Input() earthquakes: EarthquakeListResponse | null = null;
  @Input() loading = false;
  @Input() error: string | null = null;
  @Output() pageChange = new EventEmitter<number>();

  onPageChange(page: number): void {
    this.pageChange.emit(page);
  }
}
