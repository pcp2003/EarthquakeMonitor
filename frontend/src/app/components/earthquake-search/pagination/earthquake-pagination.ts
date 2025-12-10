import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import './earthquake-pagination.css';

@Component({
  selector: 'app-pagination-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './earthquake-pagination.html',
  styleUrl: './earthquake-pagination.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PaginationControlComponent {
  @Input() currentPage = 1;
  @Input() hasPrevious = false;
  @Input() hasNext = false;
  @Output() pageChange = new EventEmitter<number>();

  onPreviousPage(): void {
    if (this.hasPrevious) {
      this.pageChange.emit(this.currentPage - 1);
    }
  }

  onNextPage(): void {
    if (this.hasNext) {
      this.pageChange.emit(this.currentPage + 1);
    }
  }
}
