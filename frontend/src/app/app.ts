import { Component, signal } from '@angular/core';
import { EarthquakeSearchComponent } from './components/earthquake-search/earthquake-search';

@Component({
  selector: 'app-root',
  imports: [EarthquakeSearchComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
