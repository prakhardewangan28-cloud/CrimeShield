import { request } from './apiClient';
import type { HealthResponse } from '../types';

export const healthService = {
  async checkHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/api/health', {
      method: 'GET',
      timeoutMs: 3000
    });
  }
};
