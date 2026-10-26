import { request } from './apiClient';
import type { Evidence, EvidenceCreatePayload, EvidenceUpdatePayload, EvidenceStatistics } from '../types';

export const evidenceService = {
  async getEvidence(params?: { evidence_type?: string; processing_status?: string }): Promise<{ evidence: Evidence[]; count: number }> {
    return request<{ evidence: Evidence[]; count: number }>('/api/evidence', {
      method: 'GET',
      params
    });
  },

  async getEvidenceById(evidenceId: number | string): Promise<{ evidence: Evidence }> {
    return request<{ evidence: Evidence }>(`/api/evidence/${evidenceId}`, {
      method: 'GET'
    });
  },

  async getCaseEvidence(caseId: number | string): Promise<{ case_id: number; evidence: Evidence[]; count: number }> {
    return request<{ case_id: number; evidence: Evidence[]; count: number }>(`/api/cases/${caseId}/evidence`, {
      method: 'GET'
    });
  },

  async createEvidence(payload: EvidenceCreatePayload): Promise<{ message: string; evidence: Evidence }> {
    return request<{ message: string; evidence: Evidence }>('/api/evidence', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateEvidence(evidenceId: number | string, payload: EvidenceUpdatePayload): Promise<{ message: string; evidence: Evidence }> {
    return request<{ message: string; evidence: Evidence }>(`/api/evidence/${evidenceId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteEvidence(evidenceId: number | string): Promise<{ message: string }> {
    return request<{ message: string }>(`/api/evidence/${evidenceId}`, {
      method: 'DELETE'
    });
  },

  async getStatistics(): Promise<{ statistics: EvidenceStatistics }> {
    return request<{ statistics: EvidenceStatistics }>('/api/evidence/statistics', {
      method: 'GET'
    });
  }
};
