import { HealthResponse } from '../types/api';

const API_BASE = '/api/v1';

export class ApiService {
  /**
   * Fetches backend and database health status
   */
  static async getHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      let errorMessage = `Server returned status ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData?.error?.message) {
          errorMessage = errorData.error.message;
        }
      } catch {
        // Fallback to HTTP error
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }
}
