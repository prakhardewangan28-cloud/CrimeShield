import { request } from './apiClient';
import type { Case, CaseCreatePayload, CaseUpdatePayload, CaseStatistics } from '../types';

export const caseService = {
  async getCases(params?: { title?: string; location?: string; status?: string }): Promise<{ cases: Case[]; count: number }> {
    return request<{ cases: Case[]; count: number }>('/api/cases', {
      method: 'GET',
      params
    });
  },

  async getCaseById(caseId: number | string): Promise<{ case: Case }> {
    return request<{ case: Case }>(`/api/cases/${caseId}`, {
      method: 'GET'
    });
  },

  async getCaseByCode(caseCode: string): Promise<{ case: Case }> {
    return request<{ case: Case }>(`/api/cases/code/${encodeURIComponent(caseCode)}`, {
      method: 'GET'
    });
  },

  async createCase(payload: CaseCreatePayload): Promise<{ message: string; case: Case }> {
    return request<{ message: string; case: Case }>('/api/cases', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateCase(caseId: number | string, payload: CaseUpdatePayload): Promise<{ message: string; case: Case }> {
    return request<{ message: string; case: Case }>(`/api/cases/${caseId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteCase(caseId: number | string): Promise<{ message: string }> {
    return request<{ message: string }>(`/api/cases/${caseId}`, {
      method: 'DELETE'
    });
  },

  async getStatistics(): Promise<{ statistics: CaseStatistics }> {
    return request<{ statistics: CaseStatistics }>('/api/cases/statistics', {
      method: 'GET'
    });
  }
};
