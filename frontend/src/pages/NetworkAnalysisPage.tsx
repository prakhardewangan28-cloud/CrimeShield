import React, { useEffect, useState, useCallback } from 'react';
import {
  Share2,
  Play,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  GitMerge,
  Clock,
  Layers,
  ArrowRight,
  ShieldAlert,
  Info,
  ExternalLink,
  Filter
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { caseService } from '../services/caseService';
import { connectionService } from '../services/connectionService';
import { analysisService } from '../services/analysisService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { NetworkGraph } from '../components/network/NetworkGraph';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import { ErrorState } from '../components/common/ErrorState';
import type { Case, Connection, AnalysisRunResult } from '../types';

export const NetworkAnalysisPage: React.FC = () => {
  const { addToast } = useBackendStatus();

  const [cases, setCases] = useState<Case[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Analysis result
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisRunResult | null>(null);

  // Selected for inspection
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null);

  // Quick review modal in graph
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviewStatus, setReviewStatus] = useState<'confirmed_for_review' | 'dismissed'>('confirmed_for_review');
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  // Load Graph Data
  const loadGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [casesRes, connRes] = await Promise.all([
        caseService.getCases(),
        connectionService.getConnections()
      ]);
      setCases(casesRes.cases);
      setConnections(connRes.connections);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load network intelligence graph');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGraphData();
  }, [loadGraphData]);

  // Run Real Backend Analysis
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await analysisService.runAnalysis(100);
      setLastAnalysis(res.results);
      addToast(
        'success',
        'Analysis Algorithm Complete',
        `Analyzed ${res.results.evidence_count || 0} evidence items. Discovered ${res.results.connections_created || 0} new links.`
      );
      // Reload graph elements
      await loadGraphData();
    } catch (err: unknown) {
      addToast('error', 'Analysis Engine Failed', err instanceof Error ? err.message : 'Backend analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Submit Quick Review from Graph
  const handleQuickReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConnection) return;
    setIsSubmittingReview(true);
    try {
      await connectionService.updateReviewStatus(selectedConnection.id, {
        review_status: reviewStatus,
        review_notes: reviewNotes || undefined
      });
      addToast(
        'success',
        'Review Updated',
        `Connection #${selectedConnection.id} marked as ${reviewStatus.replace(/_/g, ' ')}`
      );
      setReviewModalOpen(false);
      setSelectedConnection(null);
      await loadGraphData();
    } catch (err: unknown) {
      addToast('error', 'Update Failed', err instanceof Error ? err.message : 'Could not update review status');
    } finally {
      setIsSubmittingReview(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">
            Criminal Network Analysis Workspace
          </h2>
          <p className="text-xs text-[#94A3B8]">
            Multi-entity correlation engine using Strategy Pattern to uncover hidden links across fragmented evidence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadGraphData}
            disabled={loading || isAnalyzing}
            className="p-2 rounded-lg bg-[#111C2D] border border-[#1E293B] text-[#94A3B8] hover:text-white hover:border-cyan-500/40 transition-all"
            title="Refresh Graph"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
          <button
            onClick={handleRunAnalysis}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-5 py-2.5 text-xs font-bold rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/25 active:scale-95 disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${isAnalyzing ? 'animate-pulse' : ''}`} />
            <span>{isAnalyzing ? 'Executing Correlation Engine...' : 'Run Network Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Mandatory Investigative Notice */}
      <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/40 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <strong className="text-amber-300 font-bold">Investigative Lead Notice:</strong> Potential connections identified by CRIMESHIELD are algorithmic investigative leads based on shared geographical, nominal, or telecom references, not proof of criminal activity. All findings require human review and legal verification.
        </div>
      </div>

      {/* Last Analysis Run Result Banner */}
      {lastAnalysis && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-950/40 to-[#111C2D] border border-cyan-800/40 flex flex-wrap items-center justify-between gap-4 animate-in fade-in duration-300">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h5 className="text-sm font-bold text-[#F1F5F9]">Analysis Engine Completed</h5>
              <p className="text-xs text-[#94A3B8]">
                Scanned all evidence pairs with Location (&lt;50km), Person (Normalized), and Phone strategies.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs font-mono">
            <div>
              <span className="text-[#94A3B8] block text-[10px] uppercase">Evidence Analyzed</span>
              <span className="font-bold text-slate-200">{lastAnalysis.evidence_count || 0} items</span>
            </div>
            <div>
              <span className="text-[#94A3B8] block text-[10px] uppercase">Connections Found</span>
              <span className="font-bold text-amber-400">{lastAnalysis.connections_found || 0}</span>
            </div>
            <div>
              <span className="text-[#94A3B8] block text-[10px] uppercase">New Links Created</span>
              <span className="font-bold text-emerald-400">+{lastAnalysis.connections_created || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && <ErrorState message={error} onRetry={loadGraphData} />}

      {/* Interactive Cytoscape Graph */}
      <NetworkGraph
        cases={cases}
        connections={connections}
        onSelectCase={(c) => setSelectedCase(c)}
        onSelectConnection={(conn) => {
          setSelectedConnection(conn);
          setReviewStatus(conn.review_status === 'dismissed' ? 'dismissed' : 'confirmed_for_review');
          setReviewNotes(conn.review_notes || '');
        }}
        isLoading={loading}
      />

      {/* Graph Metrics Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <span className="text-[10px] uppercase tracking-wider text-[#94A3B8] font-bold block mb-1">
            Network Nodes (Cases)
          </span>
          <span className="text-2xl font-black text-[#F1F5F9] font-mono">{cases.length}</span>
        </div>
        <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <span className="text-[10px] uppercase tracking-wider text-[#94A3B8] font-bold block mb-1">
            Network Edges (Links)
          </span>
          <span className="text-2xl font-black text-cyan-400 font-mono">{connections.length}</span>
        </div>
        <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <span className="text-[10px] uppercase tracking-wider text-[#94A3B8] font-bold block mb-1">
            Pending Analyst Review
          </span>
          <span className="text-2xl font-black text-amber-400 font-mono">
            {connections.filter((c) => c.review_status === 'pending').length}
          </span>
        </div>
        <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <span className="text-[10px] uppercase tracking-wider text-[#94A3B8] font-bold block mb-1">
            Confirmed Leads
          </span>
          <span className="text-2xl font-black text-emerald-400 font-mono">
            {connections.filter((c) => c.review_status === 'confirmed_for_review').length}
          </span>
        </div>
      </div>

      {/* Case Node Inspection Modal */}
      {selectedCase && (
        <Modal
          isOpen={!!selectedCase}
          onClose={() => setSelectedCase(null)}
          title={`Inspected Node: ${selectedCase.case_code}`}
          subtitle={`Case ID #${selectedCase.id}`}
        >
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-base font-bold text-[#F1F5F9]">{selectedCase.title}</h4>
                <StatusBadge status={selectedCase.status} type="case" />
              </div>
              <p className="text-xs text-[#94A3B8] leading-relaxed">
                {selectedCase.description || 'No detailed case summary logged'}
              </p>
              <div className="pt-2 border-t border-[#1E293B] text-xs text-[#94A3B8] flex items-center justify-between font-mono">
                <span>Location: {selectedCase.location || 'N/A'}</span>
                <span>Created: {selectedCase.created_at?.slice(0, 10) || '—'}</span>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setSelectedCase(null)}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#0D1422] border border-[#1E293B] text-[#94A3B8] hover:text-white"
              >
                Close
              </button>
              <Link
                to={`/cases?id=${selectedCase.id}`}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 flex items-center gap-1.5 shadow-md shadow-cyan-500/20"
              >
                <span>Open Full Dossier</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </Modal>
      )}

      {/* Connection Edge Inspection & Review Modal */}
      {selectedConnection && (
        <Modal
          isOpen={!!selectedConnection}
          onClose={() => setSelectedConnection(null)}
          title={`Connection Lead #${selectedConnection.id}`}
          subtitle={`Case #${selectedConnection.case_id_1} ⇄ Case #${selectedConnection.case_id_2}`}
        >
          <form onSubmit={handleQuickReviewSubmit} className="space-y-4">
            <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
              <div className="flex items-center justify-between">
                <StatusBadge status={selectedConnection.connection_type} type="type" size="md" />
                <StatusBadge status={selectedConnection.review_status} type="connection" size="md" />
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500">Algorithmic Correlation Logic</span>
                <p className="text-xs text-[#F1F5F9] mt-0.5 font-medium leading-relaxed">
                  {selectedConnection.explanation}
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-[#111C2D] border border-[#1E293B] text-xs">
                <span className="text-[#94A3B8] block text-[10px] uppercase font-semibold">Matched Identity / Value</span>
                <span className="font-mono text-cyan-300 font-bold text-sm">
                  "{selectedConnection.connection_value}"
                </span>
              </div>

              {selectedConnection.review_notes && (
                <div className="text-xs text-[#94A3B8]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Current Review Notes:</span>
                  <span className="italic">"{selectedConnection.review_notes}"</span>
                </div>
              )}
            </div>

            {/* Review Status Update Section */}
            <div className="space-y-3 pt-2">
              <h5 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                Update Operational Review Status
              </h5>

              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1">
                  Determination <span className="text-rose-400">*</span>
                </label>
                <select
                  value={reviewStatus}
                  onChange={(e) => setReviewStatus(e.target.value as any)}
                  className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
                >
                  <option value="confirmed_for_review">Confirm for Active Review (Investigative Lead)</option>
                  <option value="dismissed">Dismiss Lead (False Positive / Unrelated)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1">
                  Analyst Assessment Notes
                </label>
                <textarea
                  rows={2}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Reason for confirming or dismissing this lead..."
                  className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-[#1E293B]">
              <button
                type="button"
                onClick={() => setSelectedConnection(null)}
                disabled={isSubmittingReview}
                className="px-4 py-2 text-sm font-medium rounded-lg text-[#94A3B8] hover:text-white bg-[#0D1422] border border-[#1E293B]"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmittingReview}
                className="px-5 py-2 text-sm font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
              >
                {isSubmittingReview ? 'Submitting PATCH...' : 'Save Review Decision'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
