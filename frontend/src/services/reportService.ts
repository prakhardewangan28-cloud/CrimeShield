import { request, downloadFile } from './apiClient';
import type { SystemSummary, CaseReportInfo } from '../types';

export const reportService = {
  async getSystemSummary(): Promise<{ summary: SystemSummary }> {
    return request<{ summary: SystemSummary }>('/api/reports/summary', {
      method: 'GET'
    });
  },

  async getCaseReportInfo(caseId: number | string): Promise<CaseReportInfo> {
    return request<CaseReportInfo>(`/api/reports/cases/${caseId}`, {
      method: 'GET'
    });
  },

  async downloadCaseReportCsv(caseId: number | string, caseCode?: string): Promise<void> {
    const filename = `case_${caseCode || caseId}_report.csv`;
    return downloadFile(`/api/reports/cases/${caseId}/export?format=csv`, filename);
  },

  async downloadCaseReportTxt(caseId: number | string, caseCode?: string): Promise<void> {
    const filename = `case_${caseCode || caseId}_report.txt`;
    return downloadFile(`/api/reports/cases/${caseId}/export?format=txt`, filename);
  }
};
