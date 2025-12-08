import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { EarthquakeList } from './components/earthquake-list/earthquake-list';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, EarthquakeList],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
