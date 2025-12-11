import { Component, signal, OnInit, inject } from '@angular/core';
import { EarthquakeSearchComponent } from './components/earthquake-search/earthquake-search';
import { Scheduler } from './services/scheduler';

@Component({
  selector: 'app-root',
  imports: [EarthquakeSearchComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('frontend');
  private scheduler = inject(Scheduler);

  ngOnInit(): void {
    // Start scheduler when app loads
    this.scheduler.startScheaduler().subscribe({
      next: (response) => {
        console.log('Scheduler started:', response);
      },
      error: (error) => {
        console.error('Failed to start scheduler:', error);
      }
    });
  }
}
