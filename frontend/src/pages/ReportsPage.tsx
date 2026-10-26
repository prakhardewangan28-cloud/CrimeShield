import React, { useEffect, useState, useCallback } from 'react';
import {
  FileSpreadsheet,
  Download,
  FileText,
  RefreshCw,
  FolderOpen,
  GitMerge,
  ShieldAlert,
  CheckCircle2,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { reportService } from '../services/reportService';
import { caseService } from '../services/caseService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import type { SystemSummary, Case, CaseReportInfo } from '../types';

export const ReportsPage: React.FC = () => {
  const { addToast } = useBackendStatus();

  const [summary, setSummary] = useState<SystemSummary | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected Case for Specific Report
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null);
  const [caseReportInfo, setCaseReportInfo] = useState<CaseReportInfo | null>(null);
  const [loadingReportInfo, setLoadingReportInfo] = useState(false);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, casesRes] = await Promise.all([
        reportService.getSystemSummary(),
        caseService.getCases()
      ]);
      setSummary(sumRes.summary);
      setCases(casesRes.cases);
      if (casesRes.cases.length > 0 && selectedCaseId === null) {
        setSelectedCaseId(casesRes.cases[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve reports summary');
    } finally {
      setLoading(false);
    }
  }, [selectedCaseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // When selected case changes, fetch report metadata from /api/reports/cases/<id>
  useEffect(() => {
    if (!selectedCaseId) return;

    let isCurrent = true;
    const fetchInfo = async () => {
      setLoadingReportInfo(true);
      try {
        const info = await reportService.getCaseReportInfo(selectedCaseId);
        if (isCurrent) setCaseReportInfo(info);
      } catch {
        if (isCurrent) setCaseReportInfo(null);
      } finally {
        if (isCurrent) setLoadingReportInfo(false);
      }
    };

    fetchInfo();
    return () => {
      isCurrent = false;
    };
  }, [selectedCaseId]);

  // Handle Export
  const handleExport = async (format: 'csv' | 'txt') => {
    if (!selectedCaseId) return;
    setDownloadingFormat(format);
    try {
      const selectedCase = cases.find((c) => c.id === selectedCaseId);
      const code = selectedCase?.case_code || String(selectedCaseId);

      if (format === 'csv') {
        await reportService.downloadCaseReportCsv(selectedCaseId, code);
      } else {
        await reportService.downloadCaseReportTxt(selectedCaseId, code);
      }

      addToast(
        'success',
        'Intelligence Report Downloaded',
        `Generated case_${code}_report.${format} directly from Flask backend.`
      );
    } catch (err: unknown) {
      addToast('error', 'Export Failed', err instanceof Error ? err.message : 'Could not download report');
    } finally {
      setDownloadingFormat(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">Intelligence Reports & Forensic Export</h2>
          <p className="text-xs text-[#94A3B8]">
            Generate official court-admissible dossiers, forensic evidence summaries, and cross-case connection logs.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-[#111C2D] border border-[#1E293B] hover:border-cyan-500/40 text-[#94A3B8] hover:text-cyan-300 transition-all shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && <ErrorState message={error} onRetry={fetchData} />}

      {loading && !summary ? (
        <LoadingSkeleton rows={4} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Case Report Generator */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-6 shadow-xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#F1F5F9]">Case Intelligence Dossier Export</h3>
                  <p className="text-xs text-[#94A3B8]">
                    Select an active investigation to generate standardized evidentiary exports.
                  </p>
                </div>
              </div>

              {cases.length === 0 ? (
                <EmptyState
                  icon={<FolderOpen className="w-8 h-8" />}
                  title="No Cases to Report"
                  description="Register investigation cases first before generating formal reports."
                />
              ) : (
                <div className="space-y-5">
                  {/* Select Case */}
                  <div>
                    <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">
                      Target Investigation Case
                    </label>
                    <select
                      value={selectedCaseId || ''}
                      onChange={(e) => setSelectedCaseId(Number(e.target.value))}
                      className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3.5 py-2.5 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60 font-medium"
                    >
                      {cases.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.case_code} — {c.title} [{c.status}]
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Case Report Metadata Preview */}
                  {loadingReportInfo ? (
                    <LoadingSkeleton rows={2} />
                  ) : caseReportInfo ? (
                    <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-cyan-400">
                          {caseReportInfo.case_code}
                        </span>
                        <span className="text-[11px] text-[#94A3B8]">Case ID #{caseReportInfo.case_id}</span>
                      </div>
                      <h4 className="text-sm font-semibold text-[#F1F5F9]">
                        {caseReportInfo.title}
                      </h4>

                      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-[#1E293B] text-xs">
                        <div className="p-2.5 rounded-lg bg-[#111C2D] border border-[#1E293B]">
                          <span className="text-slate-500 block text-[10px] uppercase font-bold">Attached Evidence</span>
                          <span className="text-lg font-bold text-[#F1F5F9] font-mono">
                            {caseReportInfo.evidence_count} items
                          </span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#111C2D] border border-[#1E293B]">
                          <span className="text-slate-500 block text-[10px] uppercase font-bold">Correlated Leads</span>
                          <span className="text-lg font-bold text-violet-400 font-mono">
                            {caseReportInfo.connection_count} links
                          </span>
                        </div>
                      </div>
                    </div>
                  ) : null}

                  {/* Export Buttons */}
                  <div className="pt-2 flex flex-wrap items-center gap-3">
                    <button
                      onClick={() => handleExport('csv')}
                      disabled={downloadingFormat !== null || !selectedCaseId}
                      className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
                    >
                      <Download className={`w-4 h-4 ${downloadingFormat === 'csv' ? 'animate-bounce' : ''}`} />
                      <span>{downloadingFormat === 'csv' ? 'Generating CSV...' : 'Download CSV Dataset'}</span>
                    </button>

                    <button
                      onClick={() => handleExport('txt')}
                      disabled={downloadingFormat !== null || !selectedCaseId}
                      className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-[#111C2D] border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/10 font-bold text-xs transition-all active:scale-95 disabled:opacity-50"
                    >
                      <Download className={`w-4 h-4 ${downloadingFormat === 'txt' ? 'animate-bounce' : ''}`} />
                      <span>{downloadingFormat === 'txt' ? 'Generating TXT...' : 'Download Plain Text Report'}</span>
                    </button>
                  </div>

                  <p className="text-[11px] text-[#64748B] leading-relaxed">
                    Downloads are generated dynamically on the Flask backend with real chain of custody logs and forensic timestamps.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: System Summary Overview */}
          <div className="space-y-6">
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
              <div className="flex items-center gap-2.5">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-[#F1F5F9]">System Aggregate Intelligence</h3>
              </div>

              {summary ? (
                <div className="space-y-3 text-xs">
                  {/* Cases summary */}
                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Case Statistics</span>
                    <div className="flex justify-between text-slate-300">
                      <span>Total Cases:</span>
                      <strong className="font-mono text-[#F1F5F9]">{summary.cases.total}</strong>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Open:</span>
                      <span className="font-mono text-cyan-400">{summary.cases.open}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Under Review:</span>
                      <span className="font-mono text-amber-400">{summary.cases.under_review}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Closed Archives:</span>
                      <span className="font-mono text-slate-400">{summary.cases.closed}</span>
                    </div>
                  </div>

                  {/* Evidence summary */}
                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Evidence Breakdown</span>
                    <div className="flex justify-between text-slate-300">
                      <span>Total Items:</span>
                      <strong className="font-mono text-[#F1F5F9]">{summary.evidence.total}</strong>
                    </div>
                    {summary.evidence.by_status && (
                      <div className="flex justify-between text-slate-300">
                        <span>Verified / Processed:</span>
                        <span className="font-mono text-emerald-400">
                          {summary.evidence.by_status.processed ?? 0}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Connections summary */}
                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Connection Leads</span>
                    <div className="flex justify-between text-slate-300">
                      <span>Total Correlated Links:</span>
                      <strong className="font-mono text-violet-400">{summary.connections.total}</strong>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Confirmed for Review:</span>
                      <span className="font-mono text-emerald-400">{summary.connections.confirmed_for_review}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Pending Review:</span>
                      <span className="font-mono text-amber-400">{summary.connections.pending}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Dismissed:</span>
                      <span className="font-mono text-slate-500">{summary.connections.dismissed}</span>
                    </div>
                  </div>

                  <div className="pt-2 text-[11px] text-[#64748B] font-mono flex items-center justify-between">
                    <span>Generated At:</span>
                    <span>{summary.generated_at?.slice(0, 19).replace('T', ' ') || '—'}</span>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
