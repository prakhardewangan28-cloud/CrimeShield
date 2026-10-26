import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  GitMerge,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
  ArrowRight,
  Filter,
  Search,
  FolderOpen,
  MessageSquare,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { connectionService } from '../services/connectionService';
import { caseService } from '../services/caseService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { SearchBar } from '../components/common/SearchBar';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import type { Connection, ConnectionReviewStatus, Case } from '../types';

export const ConnectionsPage: React.FC = () => {
  const { addToast } = useBackendStatus();

  const [connections, setConnections] = useState<Connection[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Review Drawer / Modal
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null);
  const [reviewStatus, setReviewStatus] = useState<ConnectionReviewStatus>('confirmed_for_review');
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch connections and cases
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [connRes, casesRes] = await Promise.all([
        connectionService.getConnections(),
        caseService.getCases()
      ]);
      setConnections(connRes.connections);
      setCases(casesRes.cases);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve connection review queue');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Case lookup map
  const caseMap = useMemo(() => {
    const map = new Map<number, Case>();
    cases.forEach((c) => map.set(c.id, c));
    return map;
  }, [cases]);

  // Filtered connections
  const filteredConnections = useMemo(() => {
    return connections.filter((conn) => {
      const case1 = caseMap.get(conn.case_id_1);
      const case2 = caseMap.get(conn.case_id_2);

      const matchesSearch =
        searchQuery === '' ||
        conn.connection_value.toLowerCase().includes(searchQuery.toLowerCase()) ||
        conn.explanation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (conn.review_notes && conn.review_notes.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (case1 && case1.case_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (case2 && case2.case_code.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesStatus = statusFilter === 'all' || conn.review_status === statusFilter;
      const matchesType = typeFilter === 'all' || conn.connection_type.toLowerCase().includes(typeFilter.toLowerCase());

      return matchesSearch && matchesStatus && matchesType;
    });
  }, [connections, searchQuery, statusFilter, typeFilter, caseMap]);

  // Open Review Detail
  const handleOpenReview = (conn: Connection) => {
    setSelectedConnection(conn);
    setReviewStatus(conn.review_status === 'dismissed' ? 'dismissed' : 'confirmed_for_review');
    setReviewNotes(conn.review_notes || '');
  };

  // Submit Review via PATCH
  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConnection) return;

    setIsSubmitting(true);
    try {
      await connectionService.updateReviewStatus(selectedConnection.id, {
        review_status: reviewStatus,
        review_notes: reviewNotes.trim() ? reviewNotes.trim() : undefined
      });
      addToast(
        'success',
        'Review Decision Recorded',
        `Connection #${selectedConnection.id} determination saved as ${reviewStatus.replace(/_/g, ' ')}`
      );
      setSelectedConnection(null);
      await fetchData();
    } catch (err: unknown) {
      addToast('error', 'Review Failed', err instanceof Error ? err.message : 'Could not submit review determination');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">Connections & Leads Review Queue</h2>
          <p className="text-xs text-[#94A3B8]">
            Analyst adjudication workflow for potential cross-case correlations identified by algorithm.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 rounded-lg bg-[#111C2D] border border-[#1E293B] text-[#94A3B8] hover:text-white hover:border-cyan-500/40 transition-all"
            title="Refresh Leads"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
          <Link
            to="/network"
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg bg-[#111C2D] border border-[#1E293B] hover:border-cyan-500/40 text-[#94A3B8] hover:text-cyan-300 transition-all"
          >
            <span>Network Visualizer</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B] grid grid-cols-1 sm:grid-cols-3 gap-3">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search by value, explanation, or case code..."
        />

        {/* Review Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">All Review Statuses</option>
          <option value="pending">Pending Review</option>
          <option value="confirmed_for_review">Confirmed for Review (Verified Lead)</option>
          <option value="dismissed">Dismissed (False Positive)</option>
        </select>

        {/* Connection Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">All Connection Types</option>
          <option value="person">Person Match</option>
          <option value="location">Location Match (&lt;50km)</option>
          <option value="phone">Phone Match</option>
        </select>
      </div>

      {/* Main Table */}
      {loading && connections.length === 0 ? (
        <LoadingSkeleton rows={5} />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchData} />
      ) : filteredConnections.length === 0 ? (
        <EmptyState
          icon={<GitMerge className="w-10 h-10" />}
          title="No Connection Leads in Queue"
          description={
            searchQuery || statusFilter !== 'all'
              ? 'No matching leads found with active filters.'
              : 'Execute Network Analysis in the workspace to scan evidence for multi-entity correlations.'
          }
          actionLabel="Go to Network Analysis"
          onAction={() => window.location.assign('/network')}
        />
      ) : (
        <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#0D1422] text-[#94A3B8] text-xs font-semibold uppercase tracking-wider border-b border-[#1E293B]">
                <tr>
                  <th className="py-3.5 px-4">Lead ID</th>
                  <th className="py-3.5 px-4">Related Cases</th>
                  <th className="py-3.5 px-4">Correlation Type</th>
                  <th className="py-3.5 px-4">Shared Value & Reason</th>
                  <th className="py-3.5 px-4">Review Status</th>
                  <th className="py-3.5 px-4">Detected Date</th>
                  <th className="py-3.5 px-4 text-right">Adjudication</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B] text-[#F1F5F9]">
                {filteredConnections.map((conn) => {
                  const case1 = caseMap.get(conn.case_id_1);
                  const case2 = caseMap.get(conn.case_id_2);

                  return (
                    <tr key={conn.id} className="hover:bg-[#162338]/50 transition-colors group">
                      <td className="py-3.5 px-4 whitespace-nowrap font-mono text-xs text-[#94A3B8]">
                        #{conn.id}
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 text-xs font-mono">
                          <Link
                            to={`/cases?id=${conn.case_id_1}`}
                            className="font-bold text-cyan-400 hover:underline"
                            title={case1?.title}
                          >
                            {case1?.case_code || `Case #${conn.case_id_1}`}
                          </Link>
                          <span className="text-slate-500">⇄</span>
                          <Link
                            to={`/cases?id=${conn.case_id_2}`}
                            className="font-bold text-cyan-400 hover:underline"
                            title={case2?.title}
                          >
                            {case2?.case_code || `Case #${conn.case_id_2}`}
                          </Link>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <StatusBadge status={conn.connection_type} type="type" />
                      </td>

                      <td className="py-3.5 px-4 max-w-sm">
                        <div className="font-semibold text-xs text-[#F1F5F9] font-mono">
                          "{conn.connection_value}"
                        </div>
                        <div className="text-xs text-[#94A3B8] truncate mt-0.5">
                          {conn.explanation}
                        </div>
                        {conn.review_notes && (
                          <div className="text-[11px] text-amber-300/80 italic mt-0.5">
                            Note: {conn.review_notes}
                          </div>
                        )}
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <StatusBadge status={conn.review_status} type="connection" />
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap text-xs text-[#94A3B8] font-mono">
                        {conn.created_at ? conn.created_at.slice(0, 19).replace('T', ' ') : '—'}
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => handleOpenReview(conn)}
                          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#0D1422] border border-[#1E293B] text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-500/40 transition-all"
                        >
                          Review Lead
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 border-t border-[#1E293B] bg-[#0D1422] text-xs text-[#94A3B8] flex items-center justify-between">
            <span>Showing {filteredConnections.length} of {connections.length} detected links</span>
            <span className="font-mono">SQLite connections table</span>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {selectedConnection && (
        <Modal
          isOpen={!!selectedConnection}
          onClose={() => setSelectedConnection(null)}
          title={`Adjudicate Investigative Lead #${selectedConnection.id}`}
          subtitle="Submit formal analyst review determination to the backend."
        >
          <form onSubmit={handleSubmitReview} className="space-y-4">
            {/* Context Dossier Cards */}
            <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
              <div className="flex items-center justify-between">
                <StatusBadge status={selectedConnection.connection_type} type="type" size="md" />
                <StatusBadge status={selectedConnection.review_status} type="connection" size="md" />
              </div>

              {/* Related Cases overview */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-lg bg-[#111C2D] border border-[#1E293B]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Case 1</span>
                  <span className="font-mono text-xs font-bold text-cyan-300 block">
                    {caseMap.get(selectedConnection.case_id_1)?.case_code || `Case #${selectedConnection.case_id_1}`}
                  </span>
                  <span className="text-xs text-[#94A3B8] truncate block mt-0.5">
                    {caseMap.get(selectedConnection.case_id_1)?.title || 'No Title'}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-[#111C2D] border border-[#1E293B]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Case 2</span>
                  <span className="font-mono text-xs font-bold text-cyan-300 block">
                    {caseMap.get(selectedConnection.case_id_2)?.case_code || `Case #${selectedConnection.case_id_2}`}
                  </span>
                  <span className="text-xs text-[#94A3B8] truncate block mt-0.5">
                    {caseMap.get(selectedConnection.case_id_2)?.title || 'No Title'}
                  </span>
                </div>
              </div>

              {/* Algorithmic Reason */}
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500">Algorithmic Correlation Explanation</span>
                <p className="text-xs text-[#F1F5F9] mt-0.5 leading-relaxed font-medium">
                  {selectedConnection.explanation}
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-[#111C2D] border border-[#1E293B] text-xs">
                <span className="text-[#94A3B8] block text-[10px] uppercase font-semibold">Correlated Shared Value</span>
                <span className="font-mono text-cyan-400 font-bold text-sm">
                  "{selectedConnection.connection_value}"
                </span>
              </div>
            </div>

            {/* Review Determination Inputs */}
            <div className="space-y-3 pt-1">
              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
                  Analyst Determination <span className="text-rose-400">*</span>
                </label>
                <select
                  value={reviewStatus}
                  onChange={(e) => setReviewStatus(e.target.value as ConnectionReviewStatus)}
                  className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
                >
                  <option value="confirmed_for_review">
                    Confirmed for Review (Actionable Investigative Lead)
                  </option>
                  <option value="dismissed">
                    Dismissed (Incidental Match / Disproven / False Positive)
                  </option>
                  <option value="pending">
                    Pending Further Evidence Admissibility
                  </option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
                  Formal Review Notes / Legal Audit Log
                </label>
                <textarea
                  rows={3}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Document why this lead is confirmed or dismissed (recorded in audit logs)..."
                  className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-[#1E293B]">
              <button
                type="button"
                onClick={() => setSelectedConnection(null)}
                disabled={isSubmitting}
                className="px-4 py-2 text-sm font-medium rounded-lg text-[#94A3B8] hover:text-white bg-[#0D1422] border border-[#1E293B]"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-5 py-2 text-sm font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
              >
                {isSubmitting ? 'Recording PATCH...' : 'Submit Determination'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
