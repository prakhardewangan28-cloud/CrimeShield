import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderOpen,
  FileText,
  Share2,
  GitMerge,
  FileSpreadsheet,
  Activity,
  Shield,
  Menu,
  X,
  RefreshCw,
  Wifi,
  WifiOff,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { useBackendStatus } from '../context/BackendStatusContext';
import { ToastContainer } from '../components/common/ToastContainer';

export const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { status, latencyMs, refreshHealth } = useBackendStatus();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const location = useLocation();

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await refreshHealth();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/cases', label: 'Case Management', icon: FolderOpen },
    { to: '/evidence', label: 'Evidence Vault', icon: FileText },
    { to: '/network', label: 'Network Analysis', icon: Share2 },
    { to: '/connections', label: 'Connections Review', icon: GitMerge },
    { to: '/reports', label: 'Intelligence Reports', icon: FileSpreadsheet },
    { to: '/health', label: 'System Health & API', icon: Activity }
  ];

  // Derive current page title
  const currentNav = navItems.find((item) =>
    item.to === '/' ? location.pathname === '/' : location.pathname.startsWith(item.to)
  );
  const pageTitle = currentNav?.label || 'CRIMESHIELD';

  return (
    <div className="flex h-screen bg-[#080D18] text-[#F1F5F9] overflow-hidden">
      {/* Toast notifications */}
      <ToastContainer />

      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col w-72 bg-[#0D1422] border-r border-[#1E293B] transition-transform duration-300 lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand */}
        <div className="p-6 border-b border-[#1E293B]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-cyan-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-extrabold tracking-wider text-base text-[#F1F5F9]">
                  CRIME<span className="text-cyan-400">SHIELD</span>
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  v3.0
                </span>
              </div>
              <p className="text-[11px] text-[#94A3B8] truncate leading-tight mt-0.5 font-medium">
                Connected Intelligence System
              </p>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-[#94A3B8] hover:text-white p-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="mt-3 p-2 rounded-lg bg-[#111C2D] border border-[#1E293B] text-[11px] text-[#94A3B8]">
            <span className="text-cyan-400 font-semibold">Tagline:</span> From Fragmented Evidence to Connected Intelligence
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_-3px_rgba(34,211,238,0.2)]'
                      : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#111C2D] border border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-cyan-400' : 'text-[#94A3B8] group-hover:text-cyan-300'}`} />
                    <span className="flex-1">{item.label}</span>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-cyan-400" />}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-[#1E293B] bg-[#090E18]">
          <div className="p-3 rounded-xl bg-[#111C2D] border border-[#1E293B] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              {status === 'connected' ? (
                <div className="relative flex items-center justify-center">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  <span className="absolute w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping opacity-75" />
                </div>
              ) : (
                <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              )}
              <div>
                <p className="text-xs font-semibold text-[#F1F5F9]">
                  {status === 'connected' ? 'Flask API Online' : 'API Offline'}
                </p>
                <p className="text-[10px] text-[#94A3B8] font-mono">
                  {status === 'connected' && latencyMs !== null ? `${latencyMs}ms • 127.0.0.1:5000` : 'python app.py'}
                </p>
              </div>
            </div>
            <button
              onClick={handleManualRefresh}
              title="Ping Backend"
              className={`p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors ${
                isRefreshing ? 'animate-spin text-cyan-400' : ''
              }`}
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="mt-2 text-center">
            <span className="text-[10px] text-[#64748B] font-mono">
              College Advanced Python Project
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Shell */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-[#0D1422] border-b border-[#1E293B] px-6 flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B]"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-extrabold text-[#F1F5F9] tracking-tight flex items-center gap-2">
                {pageTitle}
              </h1>
              <div className="flex items-center gap-1.5 text-xs text-[#94A3B8]">
                <span>CRIMESHIELD</span>
                <span>/</span>
                <span className="text-cyan-400">{pageTitle}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Status Indicator Pill */}
            <div
              className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium ${
                status === 'connected'
                  ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/50'
                  : 'bg-rose-950/40 text-rose-300 border-rose-800/50'
              }`}
            >
              {status === 'connected' ? (
                <>
                  <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Backend Live ({latencyMs}ms)</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                  <span>Backend Disconnected</span>
                </>
              )}
            </div>

            {/* Refresh Action */}
            <button
              onClick={handleManualRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#111C2D] border border-[#1E293B] hover:border-cyan-500/40 hover:text-cyan-300 text-[#94A3B8] transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
              <span className="hidden md:inline">Sync API</span>
            </button>

            {/* Academic Tag */}
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-violet-950/30 border border-violet-800/40 text-violet-300 text-xs font-medium">
              <Sparkles className="w-3 h-3 text-violet-400" />
              <span>Advanced Python 2026</span>
            </div>
          </div>
        </header>

        {/* Page Content Body */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[#080D18]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
