import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FolderOpen,
  FileText,
  GitMerge,
  AlertCircle,
  Clock,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Server,
  ShieldAlert,
  Search
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { reportService } from '../services/reportService';
import { caseService } from '../services/caseService';
import { connectionService } from '../services/connectionService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorState } from '../components/common/ErrorState';
import { DemoModeBanner } from '../components/common/DemoModeBanner';
import type { SystemSummary, Case, Connection } from '../types';

export const DashboardPage: React.FC = () => {
  const { status, latencyMs } = useBackendStatus();
  const [summary, setSummary] = useState<SystemSummary | null>(null);
  const [recentCases, setRecentCases] = useState<Case[]>([]);
  const [recentConnections, setRecentConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch system summary
      const summaryRes = await reportService.getSystemSummary();
      setSummary(summaryRes.summary);

      // 2. Fetch recent cases
      const casesRes = await caseService.getCases();
      setRecentCases(casesRes.cases.slice(0, 5));

      // 3. Fetch recent connections
      const connRes = await connectionService.getConnections();
      setRecentConnections(connRes.connections.slice(0, 5));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve dashboard intelligence');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Chart data for case statuses
  const caseStatusData = summary
    ? [
        { name: 'Open', value: summary.cases.open || 0, color: '#22D3EE' },
        { name: 'Under Review', value: summary.cases.under_review || 0, color: '#F59E0B' },
        { name: 'Closed', value: summary.cases.closed || 0, color: '#64748B' }
      ]
    : [];

  // Chart data for evidence types
  const evidenceTypeData = summary?.evidence.by_type
    ? Object.entries(summary.evidence.by_type).map(([key, val]) => ({
        type: key.charAt(0).toUpperCase() + key.slice(1),
        count: val
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* College Presentation Guide Banner */}
      <DemoModeBanner />

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9] tracking-tight">
            Criminal Intelligence Operations Center
          </h2>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Real-time multi-source case aggregation, evidence linking, and relational intelligence.
          </p>
        </div>
        <button
          onClick={fetchDashboardData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-[#111C2D] border border-[#1E293B] hover:border-cyan-500/40 hover:text-cyan-300 text-[#94A3B8] transition-all shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Refresh Intelligence</span>
        </button>
      </div>

      {/* Error state */}
      {error && (
        <ErrorState
          title="Intelligence Feed Error"
          message={error}
          onRetry={fetchDashboardData}
        />
      )}

      {/* Loading Skeleton */}
      {loading && !summary ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-28 bg-[#111C2D] border border-[#1E293B] rounded-xl animate-pulse" />
            ))}
          </div>
          <LoadingSkeleton rows={4} />
        </div>
      ) : (
        <>
          {/* Top Operational Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Total Cases"
              value={summary?.cases.total ?? 0}
              subtext={`${summary?.cases.open ?? 0} active investigations`}
              icon={<FolderOpen className="w-5 h-5" />}
              color="cyan"
            />
            <StatCard
              label="Cases Under Review"
              value={summary?.cases.under_review ?? 0}
              subtext={`${summary?.cases.closed ?? 0} closed archives`}
              icon={<Clock className="w-5 h-5" />}
              color="amber"
            />
            <StatCard
              label="Evidence Records"
              value={summary?.evidence.total ?? 0}
              subtext={`${summary?.evidence.by_status?.processed ?? 0} verified references`}
              icon={<FileText className="w-5 h-5" />}
              color="blue"
            />
            <StatCard
              label="Potential Links"
              value={summary?.connections.total ?? 0}
              subtext={`${summary?.connections.confirmed_for_review ?? 0} confirmed leads`}
              icon={<GitMerge className="w-5 h-5" />}
              color="violet"
            />
          </div>

          {/* Visual Analytics Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Case Status Distribution Donut */}
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-[#F1F5F9]">Case Status Breakdown</h3>
                  <p className="text-xs text-[#94A3B8]">Operational workflow status</p>
                </div>
                <TrendingUp className="w-4 h-4 text-cyan-400" />
              </div>

              <div className="flex-1 min-h-[220px] relative flex items-center justify-center">
                {caseStatusData.every((d) => d.value === 0) ? (
                  <p className="text-xs text-[#94A3B8]">No cases logged yet</p>
                ) : (
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={caseStatusData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={80}
                        paddingAngle={4}
                      >
                        {caseStatusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0D1422',
                          borderColor: '#1E293B',
                          borderRadius: '8px',
                          color: '#F1F5F9',
                          fontSize: '12px'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>

              <div className="flex justify-around pt-3 border-t border-[#1E293B] text-xs">
                {caseStatusData.map((item) => (
                  <div key={item.name} className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-[#94A3B8]">{item.name}:</span>
                    <span className="font-bold text-[#F1F5F9] font-mono">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence by Type Bar Chart */}
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-[#F1F5F9]">Evidence Vault Categories</h3>
                  <p className="text-xs text-[#94A3B8]">Distribution by forensic discipline</p>
                </div>
                <FileText className="w-4 h-4 text-blue-400" />
              </div>

              <div className="flex-1 min-h-[220px]">
                {evidenceTypeData.length === 0 ? (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-xs text-[#94A3B8]">No evidence cataloged</p>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={evidenceTypeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis dataKey="type" stroke="#94A3B8" fontSize={10} tickLine={false} />
                      <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0D1422',
                          borderColor: '#1E293B',
                          borderRadius: '8px',
                          color: '#F1F5F9',
                          fontSize: '12px'
                        }}
                      />
                      <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>

              <div className="pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs text-[#94A3B8]">
                <span>Total Items: <strong className="text-[#F1F5F9] font-mono">{summary?.evidence.total ?? 0}</strong></span>
                <Link to="/evidence" className="text-cyan-400 hover:underline flex items-center gap-1">
                  Vault <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>

            {/* Backend System & Engine Status */}
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-[#F1F5F9]">Backend Architecture</h3>
                    <p className="text-xs text-[#94A3B8]">Flask 3.0 + SQLite3 Engine</p>
                  </div>
                  <Server className="w-4 h-4 text-cyan-400" />
                </div>

                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between">
                    <span className="text-xs text-[#94A3B8]">Flask REST Status:</span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                      {status === 'connected' ? 'Operational' : 'Unavailable'}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between">
                    <span className="text-xs text-[#94A3B8]">API Latency:</span>
                    <span className="text-xs font-mono font-bold text-cyan-400">
                      {latencyMs !== null ? `${latencyMs} ms` : 'N/A'}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between">
                    <span className="text-xs text-[#94A3B8]">Matching Algorithm:</span>
                    <span className="text-xs font-mono text-violet-300">
                      Strategy Pattern
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between">
                    <span className="text-xs text-[#94A3B8]">Active Rules:</span>
                    <span className="text-xs text-[#F1F5F9]">
                      Geo &lt;50km • Person • Phone
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-[#1E293B] flex items-center justify-between">
                <Link
                  to="/health"
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
                >
                  Inspect API Routes <ArrowRight className="w-3 h-3" />
                </Link>
                <Link
                  to="/network"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-colors shadow-md shadow-cyan-500/20"
                >
                  Run Analysis
                </Link>
              </div>
            </div>
          </div>

          {/* Dual Tables: Recent Cases & Detected Connections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Cases */}
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-[#F1F5F9]">Active Investigations</h3>
                  <p className="text-xs text-[#94A3B8]">Latest registered criminal cases</p>
                </div>
                <Link
                  to="/cases"
                  className="text-xs font-semibold text-cyan-400 hover:underline flex items-center gap-1"
                >
                  View All ({summary?.cases.total ?? 0}) <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              {recentCases.length === 0 ? (
                <div className="py-8 text-center text-xs text-[#94A3B8]">
                  No cases registered in database.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {recentCases.map((c) => (
                    <div
                      key={c.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] hover:border-cyan-500/30 transition-colors"
                    >
                      <div className="min-w-0 flex-1 mr-3">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-cyan-400">
                            {c.case_code}
                          </span>
                          <StatusBadge status={c.status} type="case" size="sm" />
                        </div>
                        <h5 className="text-xs font-medium text-[#F1F5F9] truncate mt-1">
                          {c.title}
                        </h5>
                        <p className="text-[11px] text-[#94A3B8] truncate">
                          {c.location || 'Location Unspecified'}
                        </p>
                      </div>
                      <Link
                        to={`/cases?id=${c.id}`}
                        className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Connections */}
            <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-[#F1F5F9]">Detected Investigative Leads</h3>
                  <p className="text-xs text-[#94A3B8]">Cross-case evidence correlations</p>
                </div>
                <Link
                  to="/connections"
                  className="text-xs font-semibold text-violet-400 hover:underline flex items-center gap-1"
                >
                  Review ({summary?.connections.total ?? 0}) <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              {recentConnections.length === 0 ? (
                <div className="py-8 text-center text-xs text-[#94A3B8]">
                  No potential connections detected. Run network analysis to correlate evidence.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {recentConnections.map((conn) => (
                    <div
                      key={conn.id}
                      className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] hover:border-violet-500/30 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                          <StatusBadge status={conn.connection_type} type="type" size="sm" />
                          <span className="text-[11px] font-mono text-[#94A3B8]">
                            Case #{conn.case_id_1} ⇄ Case #{conn.case_id_2}
                          </span>
                        </div>
                        <StatusBadge status={conn.review_status} type="connection" size="sm" />
                      </div>
                      <p className="text-xs text-[#F1F5F9] line-clamp-1">
                        {conn.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
