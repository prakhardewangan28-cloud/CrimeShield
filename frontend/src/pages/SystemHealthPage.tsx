import React, { useEffect, useState } from 'react';
import {
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Server,
  Database,
  Terminal,
  Shield,
  Layers,
  Code,
  Copy,
  ExternalLink
} from 'lucide-react';
import { healthService } from '../services/healthService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { API_BASE_URL } from '../services/apiClient';

interface EndpointCheck {
  method: string;
  path: string;
  description: string;
  status: 'pending' | 'ok' | 'error';
  latency?: number;
  responsePreview?: string;
}

export const SystemHealthPage: React.FC = () => {
  const { status, health, latencyMs, refreshHealth, addToast } = useBackendStatus();
  const [checking, setChecking] = useState(false);

  const [endpoints, setEndpoints] = useState<EndpointCheck[]>([
    { method: 'GET', path: '/api/health', description: 'System health & uptime', status: 'pending' },
    { method: 'GET', path: '/api/cases', description: 'Fetch all case dossiers', status: 'pending' },
    { method: 'GET', path: '/api/cases/statistics', description: 'Case status metrics aggregation', status: 'pending' },
    { method: 'GET', path: '/api/evidence', description: 'Fetch evidence vault items', status: 'pending' },
    { method: 'GET', path: '/api/evidence/statistics', description: 'Evidence category counts', status: 'pending' },
    { method: 'GET', path: '/api/connections', description: 'Fetch detected correlation leads', status: 'pending' },
    { method: 'GET', path: '/api/connections/statistics', description: 'Connection status counts', status: 'pending' },
    { method: 'GET', path: '/api/reports/summary', description: 'Unified system intelligence report', status: 'pending' },
  ]);

  const probeAllEndpoints = async () => {
    setChecking(true);
    await refreshHealth();

    const updated = await Promise.all(
      endpoints.map(async (ep) => {
        const start = performance.now();
        try {
          const res = await fetch(`${API_BASE_URL}${ep.path}`);
          const elapsed = Math.round(performance.now() - start);
          if (res.ok) {
            const data = await res.json();
            return {
              ...ep,
              status: 'ok' as const,
              latency: elapsed,
              responsePreview: JSON.stringify(data).slice(0, 100) + '...'
            };
          } else {
            return {
              ...ep,
              status: 'error' as const,
              latency: elapsed,
              responsePreview: `Status ${res.status}`
            };
          }
        } catch (err: unknown) {
          return {
            ...ep,
            status: 'error' as const,
            responsePreview: err instanceof Error ? err.message : 'Connection refused'
          };
        }
      })
    );

    setEndpoints(updated);
    setChecking(false);
  };

  useEffect(() => {
    probeAllEndpoints();
  }, []);

  const copyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    addToast('info', 'Command Copied', cmd);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">System Health & REST API Diagnostic Suite</h2>
          <p className="text-xs text-[#94A3B8]">
            Automated verification of Flask HTTP server, CORS middleware, and SQLite3 database connectivity.
          </p>
        </div>
        <button
          onClick={probeAllEndpoints}
          disabled={checking}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />
          <span>Probe All Endpoints</span>
        </button>
      </div>

      {/* Main Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Connection State */}
        <div className="p-5 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#94A3B8]">Backend Status</span>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2.5">
            <span className={`w-3 h-3 rounded-full ${status === 'connected' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-xl font-black text-[#F1F5F9] capitalize">{status}</span>
          </div>
          <p className="text-xs text-[#94A3B8] font-mono mt-2">
            Base URL: {API_BASE_URL}
          </p>
        </div>

        {/* Latency */}
        <div className="p-5 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#94A3B8]">Round-Trip Latency</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <span className="text-2xl font-black text-[#F1F5F9] font-mono">
            {latencyMs !== null ? `${latencyMs} ms` : '—'}
          </span>
          <p className="text-xs text-[#94A3B8] mt-2">
            {latencyMs !== null && latencyMs < 50 ? 'Optimal Localhost Latency' : 'Real-time HTTP polling'}
          </p>
        </div>

        {/* Database */}
        <div className="p-5 rounded-xl bg-[#111C2D] border border-[#1E293B]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#94A3B8]">Database Architecture</span>
            <Database className="w-4 h-4 text-violet-400" />
          </div>
          <span className="text-xl font-black text-violet-300 font-mono">SQLite3</span>
          <p className="text-xs text-[#94A3B8] mt-2 truncate">
            Schema: cases, evidence, connections, audit_logs
          </p>
        </div>
      </div>

      {/* Endpoint Probe Results Table */}
      <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 bg-[#0D1422] border-b border-[#1E293B] flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#F1F5F9]">Registered API Endpoints Verification</h3>
          <span className="text-xs text-[#94A3B8] font-mono">
            {endpoints.filter((e) => e.status === 'ok').length} / {endpoints.length} operational
          </span>
        </div>

        <div className="divide-y divide-[#1E293B]">
          {endpoints.map((ep) => (
            <div key={ep.path} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800">
                  {ep.method}
                </span>
                <span className="font-mono font-semibold text-[#F1F5F9]">{ep.path}</span>
                <span className="text-[#94A3B8] hidden md:inline">— {ep.description}</span>
              </div>

              <div className="flex items-center gap-4">
                {ep.latency && (
                  <span className="font-mono text-[#94A3B8]">{ep.latency}ms</span>
                )}
                {ep.status === 'ok' ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 200 OK
                  </span>
                ) : ep.status === 'error' ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/60 text-rose-300 border border-rose-800/60">
                    <XCircle className="w-3.5 h-3.5" /> Offline
                  </span>
                ) : (
                  <span className="text-slate-500 font-mono">Checking...</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* College Presentation & Demonstration Script Helper */}
      <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-[#F1F5F9]">College Viva & Testing Commands</h3>
        </div>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Use these commands during your college evaluation to demonstrate the running Flask server and backend test suite.
        </p>

        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between font-mono text-xs">
            <span className="text-slate-300">python app.py</span>
            <button
              onClick={() => copyCommand('python app.py')}
              className="text-[#94A3B8] hover:text-cyan-400 p-1"
              title="Copy"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between font-mono text-xs">
            <span className="text-slate-300">pytest -v</span>
            <button
              onClick={() => copyCommand('pytest -v')}
              className="text-[#94A3B8] hover:text-cyan-400 p-1"
              title="Copy"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-center justify-between font-mono text-xs">
            <span className="text-slate-300">python scripts/test_api.py</span>
            <button
              onClick={() => copyCommand('python scripts/test_api.py')}
              className="text-[#94A3B8] hover:text-cyan-400 p-1"
              title="Copy"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
