import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';


@Injectable({
  providedIn: 'root',
})
export class Scheduler {

  private readonly apiUrl = '/api/v1/scheduler';

  constructor(private http: HttpClient) { }

  startScheaduler() {
    return this.http.post(`${this.apiUrl}/start`, {});
  }

  stopScheaduler() {
    return this.http.post(`${this.apiUrl}/stop`, {});
  }
  
}
