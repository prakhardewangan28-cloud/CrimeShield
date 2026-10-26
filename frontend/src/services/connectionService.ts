import { request } from './apiClient';
import type { Connection, ConnectionReviewPayload, ConnectionStatistics, ConnectionGraphData } from '../types';

export const connectionService = {
  async getConnections(params?: { review_status?: string }): Promise<{ connections: Connection[]; count: number }> {
    return request<{ connections: Connection[]; count: number }>('/api/connections', {
      method: 'GET',
      params
    });
  },

  async getConnectionById(connectionId: number | string): Promise<{ connection: Connection }> {
    return request<{ connection: Connection }>(`/api/connections/${connectionId}`, {
      method: 'GET'
    });
  },

  async getCaseConnections(caseId: number | string): Promise<{ case_id: number; connections: Connection[]; count: number }> {
    return request<{ case_id: number; connections: Connection[]; count: number }>(`/api/cases/${caseId}/connections`, {
      method: 'GET'
    });
  },

  async updateReviewStatus(connectionId: number | string, payload: ConnectionReviewPayload): Promise<{ message: string; connection: Connection }> {
    return request<{ message: string; connection: Connection }>(`/api/connections/${connectionId}/review`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
  },

  async getStatistics(): Promise<{ statistics: ConnectionStatistics }> {
    return request<{ statistics: ConnectionStatistics }>('/api/connections/statistics', {
      method: 'GET'
    });
  },

  async getConnectionGraph(caseId: number | string, maxDepth: number = 2): Promise<ConnectionGraphData> {
    return request<ConnectionGraphData>(`/api/connections/graph/${caseId}`, {
      method: 'GET',
      params: { max_depth: maxDepth }
    });
  }
};
