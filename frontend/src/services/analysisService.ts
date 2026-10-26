import { request } from './apiClient';
import type { AnalysisRunResult } from '../types';

export const analysisService = {
  async runAnalysis(batchSize: number = 100): Promise<{ message: string; results: AnalysisRunResult }> {
    return request<{ message: string; results: AnalysisRunResult }>('/api/analysis/run', {
      method: 'POST',
      body: JSON.stringify({ batch_size: batchSize })
    });
  }
};
