import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FolderOpen,
  Plus,
  RefreshCw,
  Edit2,
  Trash2,
  Eye,
  FileText,
  GitMerge,
  Download,
  Calendar,
  MapPin,
  FileSpreadsheet,
  AlertCircle
} from 'lucide-react';
import { caseService } from '../services/caseService';
import { evidenceService } from '../services/evidenceService';
import { connectionService } from '../services/connectionService';
import { reportService } from '../services/reportService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { SearchBar } from '../components/common/SearchBar';
import { Modal } from '../components/common/Modal';
import { ConfirmationDialog } from '../components/common/ConfirmationDialog';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import type { Case, CaseStatus, Evidence, Connection, CaseCreatePayload } from '../types';

export const CasesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { addToast } = useBackendStatus();

  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [locationFilter, setLocationFilter] = useState('');

  // Modals & Panels
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editCase, setEditCase] = useState<Case | null>(null);
  const [deleteCaseTarget, setDeleteCaseTarget] = useState<Case | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedCaseDetail, setSelectedCaseDetail] = useState<Case | null>(null);
  const [caseEvidence, setCaseEvidence] = useState<Evidence[]>([]);
  const [caseConnections, setCaseConnections] = useState<Connection[]>([]);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Form State
  const [formData, setFormData] = useState<CaseCreatePayload>({
    case_code: '',
    title: '',
    description: '',
    location: '',
    status: 'open'
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch Cases
  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await caseService.getCases();
      setCases(res.cases);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cases');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  // Open details if ?id= is in query
  useEffect(() => {
    const caseId = searchParams.get('id');
    if (caseId && cases.length > 0) {
      const target = cases.find((c) => String(c.id) === caseId);
      if (target) {
        handleViewDetails(target);
      }
    }
  }, [searchParams, cases]);

  // Filtered cases
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const matchesSearch =
        searchQuery === '' ||
        c.case_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesStatus = statusFilter === 'all' || c.status === statusFilter;

      const matchesLocation =
        locationFilter === '' ||
        (c.location && c.location.toLowerCase().includes(locationFilter.toLowerCase()));

      return matchesSearch && matchesStatus && matchesLocation;
    });
  }, [cases, searchQuery, statusFilter, locationFilter]);

  // Handle View Details
  const handleViewDetails = async (caseItem: Case) => {
    setSelectedCaseDetail(caseItem);
    setLoadingDetails(true);
    try {
      const [evRes, connRes] = await Promise.all([
        evidenceService.getCaseEvidence(caseItem.id),
        connectionService.getCaseConnections(caseItem.id)
      ]);
      setCaseEvidence(evRes.evidence);
      setCaseConnections(connRes.connections);
    } catch {
      // fallback
      setCaseEvidence([]);
      setCaseConnections([]);
    } finally {
      setLoadingDetails(false);
    }
  };

  // Open Create Modal
  const handleOpenCreate = () => {
    const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
    setFormData({
      case_code: `CASE-${timestamp.slice(0, 8)}-${Math.floor(100 + Math.random() * 900)}`,
      title: '',
      description: '',
      location: '',
      status: 'open'
    });
    setFormErrors({});
    setCreateModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEdit = (caseItem: Case) => {
    setEditCase(caseItem);
    setFormData({
      case_code: caseItem.case_code,
      title: caseItem.title,
      description: caseItem.description || '',
      location: caseItem.location || '',
      status: caseItem.status
    });
    setFormErrors({});
  };

  // Form Validation
  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.case_code.trim()) errors.case_code = 'Case code is required';
    if (formData.case_code.length > 50) errors.case_code = 'Case code must be <= 50 characters';
    if (!formData.title.trim()) errors.title = 'Title is required';
    if (formData.title.length > 200) errors.title = 'Title must be <= 200 characters';
    if (formData.description && formData.description.length > 2000) {
      errors.description = 'Description must be <= 2000 characters';
    }
    if (formData.location && formData.location.length > 200) {
      errors.location = 'Location must be <= 200 characters';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Save (Create or Update)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      if (editCase) {
        await caseService.updateCase(editCase.id, formData);
        addToast('success', 'Case Updated', `Case ${formData.case_code} updated successfully`);
        setEditCase(null);
      } else {
        await caseService.createCase(formData);
        addToast('success', 'Case Created', `Case ${formData.case_code} initialized in intelligence database`);
        setCreateModalOpen(false);
      }
      await fetchCases();
    } catch (err: unknown) {
      addToast('error', 'Operation Failed', err instanceof Error ? err.message : 'Could not save case');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Confirm Delete
  const handleDeleteConfirm = async () => {
    if (!deleteCaseTarget) return;
    setIsDeleting(true);
    try {
      await caseService.deleteCase(deleteCaseTarget.id);
      addToast('success', 'Case Expunged', `Case ${deleteCaseTarget.case_code} removed`);
      setDeleteCaseTarget(null);
      if (selectedCaseDetail?.id === deleteCaseTarget.id) {
        setSelectedCaseDetail(null);
      }
      await fetchCases();
    } catch (err: unknown) {
      addToast('error', 'Delete Failed', err instanceof Error ? err.message : 'Could not delete case');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">Case Management System</h2>
          <p className="text-xs text-[#94A3B8]">
            Authoritative investigative dossier records, jurisdictional metadata, and status workflows.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchCases}
            disabled={loading}
            className="p-2 rounded-lg bg-[#111C2D] border border-[#1E293B] text-[#94A3B8] hover:text-white hover:border-cyan-500/40 transition-all"
            title="Refresh Cases"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
          <button
            onClick={handleOpenCreate}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20 active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>New Case Dossier</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B] grid grid-cols-1 sm:grid-cols-3 gap-3">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search by code, title, or summary..."
          className="col-span-1 sm:col-span-1"
        />

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">All Statuses</option>
          <option value="open">Open (Active)</option>
          <option value="under_review">Under Review</option>
          <option value="closed">Closed</option>
        </select>

        {/* Location Filter */}
        <div className="relative">
          <MapPin className="w-4 h-4 text-[#94A3B8] absolute left-3 top-3 pointer-events-none" />
          <input
            type="text"
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            placeholder="Filter location / coordinates..."
            className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg pl-9 pr-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
          />
        </div>
      </div>

      {/* Main Table or State */}
      {loading && cases.length === 0 ? (
        <LoadingSkeleton rows={5} />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchCases} />
      ) : filteredCases.length === 0 ? (
        <EmptyState
          icon={<FolderOpen className="w-10 h-10" />}
          title="No Investigation Cases Found"
          description={searchQuery || statusFilter !== 'all' ? 'Try adjusting your search filters.' : 'Initialize your first criminal dossier to begin investigations.'}
          actionLabel="Create First Case"
          onAction={handleOpenCreate}
        />
      ) : (
        <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#0D1422] text-[#94A3B8] text-xs font-semibold uppercase tracking-wider border-b border-[#1E293B]">
                <tr>
                  <th className="py-3.5 px-4">Case Code</th>
                  <th className="py-3.5 px-4">Title & Details</th>
                  <th className="py-3.5 px-4">Jurisdiction / Location</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B] text-[#F1F5F9]">
                {filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-[#162338]/50 transition-colors group">
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/40 px-2 py-1 rounded border border-cyan-800/40">
                        {c.case_code}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="font-semibold text-sm truncate">{c.title}</div>
                      {c.description && (
                        <div className="text-xs text-[#94A3B8] truncate mt-0.5">
                          {c.description}
                        </div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-xs text-[#94A3B8]">
                      {c.location ? (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                          <span>{c.location}</span>
                        </span>
                      ) : (
                        <span className="text-slate-600 italic">Not set</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <StatusBadge status={c.status} type="case" />
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-xs text-[#94A3B8] font-mono">
                      {c.created_at ? c.created_at.replace('T', ' ').slice(0, 19) : '—'}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleViewDetails(c)}
                          title="View Case Dossier"
                          className="p-1.5 rounded-lg text-[#94A3B8] hover:text-cyan-400 hover:bg-[#0D1422] transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleOpenEdit(c)}
                          title="Edit Case"
                          className="p-1.5 rounded-lg text-[#94A3B8] hover:text-blue-400 hover:bg-[#0D1422] transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeleteCaseTarget(c)}
                          title="Delete Case"
                          className="p-1.5 rounded-lg text-[#94A3B8] hover:text-rose-400 hover:bg-[#0D1422] transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 border-t border-[#1E293B] bg-[#0D1422] text-xs text-[#94A3B8] flex items-center justify-between">
            <span>Showing {filteredCases.length} of {cases.length} cases</span>
            <span className="font-mono">SQLite cases table</span>
          </div>
        </div>
      )}

      {/* Case Details Drawer / Modal */}
      {selectedCaseDetail && (
        <Modal
          isOpen={!!selectedCaseDetail}
          onClose={() => {
            setSelectedCaseDetail(null);
            setSearchParams({});
          }}
          title={`Case Dossier: ${selectedCaseDetail.case_code}`}
          subtitle={`Internal Case ID #${selectedCaseDetail.id}`}
          maxWidth="2xl"
        >
          <div className="space-y-6">
            {/* Metadata Summary */}
            <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-base font-bold text-[#F1F5F9]">{selectedCaseDetail.title}</h4>
                <StatusBadge status={selectedCaseDetail.status} type="case" size="md" />
              </div>

              {selectedCaseDetail.description && (
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  {selectedCaseDetail.description}
                </p>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-3 border-t border-[#1E293B] text-xs text-[#94A3B8]">
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Location / Geo</span>
                  <span className="font-mono text-cyan-300">{selectedCaseDetail.location || 'N/A'}</span>
                </div>
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Registered At</span>
                  <span className="font-mono text-slate-300">{selectedCaseDetail.created_at?.slice(0, 19) || '—'}</span>
                </div>
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Last Modified</span>
                  <span className="font-mono text-slate-300">{selectedCaseDetail.updated_at?.slice(0, 19) || '—'}</span>
                </div>
              </div>
            </div>

            {/* Quick Export Actions */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-cyan-950/20 border border-cyan-800/30">
              <span className="text-xs text-cyan-300 font-medium">Export Case Intelligence:</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => reportService.downloadCaseReportCsv(selectedCaseDetail.id, selectedCaseDetail.case_code)}
                  className="px-2.5 py-1 text-xs font-semibold rounded bg-[#111C2D] border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-1"
                >
                  <Download className="w-3 h-3" /> CSV
                </button>
                <button
                  onClick={() => reportService.downloadCaseReportTxt(selectedCaseDetail.id, selectedCaseDetail.case_code)}
                  className="px-2.5 py-1 text-xs font-semibold rounded bg-[#111C2D] border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-1"
                >
                  <Download className="w-3 h-3" /> TXT
                </button>
              </div>
            </div>

            {/* Related Evidence */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-[#F1F5F9] flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  Attached Evidence Records ({caseEvidence.length})
                </h5>
              </div>

              {loadingDetails ? (
                <LoadingSkeleton rows={2} />
              ) : caseEvidence.length === 0 ? (
                <div className="p-4 rounded-lg bg-[#0D1422] border border-[#1E293B] text-xs text-[#94A3B8] text-center">
                  No evidence linked to this case yet. Go to Evidence Vault to associate items.
                </div>
              ) : (
                <div className="space-y-2">
                  {caseEvidence.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-start justify-between gap-3 text-xs"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono font-bold text-cyan-400">{ev.evidence_code}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {ev.evidence_type}
                          </span>
                        </div>
                        <p className="text-[#F1F5F9]">{ev.description || 'No description provided'}</p>
                        <div className="flex flex-wrap gap-2 mt-1 text-[11px] text-[#94A3B8]">
                          {ev.person_reference && <span>Person: <strong className="text-violet-300">{ev.person_reference}</strong></span>}
                          {ev.phone_reference && <span>Phone: <strong className="text-emerald-300">{ev.phone_reference}</strong></span>}
                          {ev.location_reference && <span>Location: <strong className="text-cyan-300">{ev.location_reference}</strong></span>}
                        </div>
                      </div>
                      <StatusBadge status={ev.processing_status} type="evidence" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Potential Connections */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-[#F1F5F9] flex items-center gap-2">
                  <GitMerge className="w-4 h-4 text-violet-400" />
                  Correlated Cross-Case Connections ({caseConnections.length})
                </h5>
              </div>

              {caseConnections.length === 0 ? (
                <div className="p-4 rounded-lg bg-[#0D1422] border border-[#1E293B] text-xs text-[#94A3B8] text-center">
                  No connection leads detected for this case. Run Network Analysis to discover cross-case correlations.
                </div>
              ) : (
                <div className="space-y-2">
                  {caseConnections.map((conn) => {
                    const otherCaseId = conn.case_id_1 === selectedCaseDetail.id ? conn.case_id_2 : conn.case_id_1;
                    return (
                      <div
                        key={conn.id}
                        className="p-3 rounded-lg bg-[#0D1422] border border-[#1E293B] flex items-start justify-between gap-3 text-xs"
                      >
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <StatusBadge status={conn.connection_type} type="type" size="sm" />
                            <span className="text-[#94A3B8] font-mono">Linked to Case #{otherCaseId}</span>
                          </div>
                          <p className="text-[#F1F5F9]">{conn.explanation}</p>
                          <p className="text-[11px] text-slate-500 font-mono mt-0.5">Shared Value: "{conn.connection_value}"</p>
                        </div>
                        <StatusBadge status={conn.review_status} type="connection" />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}

      {/* Create / Edit Case Modal */}
      <Modal
        isOpen={createModalOpen || !!editCase}
        onClose={() => {
          setCreateModalOpen(false);
          setEditCase(null);
        }}
        title={editCase ? `Edit Case: ${editCase.case_code}` : 'Initialize New Case Dossier'}
        subtitle="Record legal and investigative metadata into SQLite database."
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Case Code */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Case Code <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={formData.case_code}
              onChange={(e) => setFormData({ ...formData, case_code: e.target.value })}
              placeholder="e.g. CASE-2026-001"
              maxLength={50}
              className={`w-full bg-[#0D1422] border rounded-lg px-3 py-2 text-sm text-[#F1F5F9] font-mono focus:outline-none ${
                formErrors.case_code ? 'border-rose-500' : 'border-[#1E293B] focus:border-cyan-500/60'
              }`}
            />
            {formErrors.case_code && (
              <p className="text-xs text-rose-400 mt-1">{formErrors.case_code}</p>
            )}
          </div>

          {/* Title */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Case Title <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g. Financial District Vault Heist"
              maxLength={200}
              className={`w-full bg-[#0D1422] border rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none ${
                formErrors.title ? 'border-rose-500' : 'border-[#1E293B] focus:border-cyan-500/60'
              }`}
            />
            {formErrors.title && (
              <p className="text-xs text-rose-400 mt-1">{formErrors.title}</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Primary Location / Coordinates
            </label>
            <input
              type="text"
              value={formData.location || ''}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="e.g. 40.7128,-74.0060 or New York City"
              maxLength={200}
              className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
            />
            <p className="text-[11px] text-[#64748B] mt-1">
              Tip: Format as latitude,longitude (e.g. 40.7128,-74.0060) to activate Geo-Distance connection matching (&lt;50km).
            </p>
          </div>

          {/* Status */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Case Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as CaseStatus })}
              className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
            >
              <option value="open">Open (Active Investigation)</option>
              <option value="under_review">Under Review (Analyst Auditing)</option>
              <option value="closed">Closed (Archived)</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Detailed Dossier Description
            </label>
            <textarea
              rows={3}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Investigation notes, initial incident overview, responding officers..."
              maxLength={2000}
              className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-[#1E293B]">
            <button
              type="button"
              onClick={() => {
                setCreateModalOpen(false);
                setEditCase(null);
              }}
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
              {isSubmitting ? 'Saving to Database...' : editCase ? 'Update Dossier' : 'Save Dossier'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={!!deleteCaseTarget}
        onClose={() => setDeleteCaseTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Expunge Criminal Case Dossier"
        message={`Are you sure you want to permanently delete case "${deleteCaseTarget?.case_code}"? This will also remove all foreign-key associated evidence and connection records in SQLite.`}
        confirmText="Permanently Expunge"
        isDanger={true}
        isLoading={isDeleting}
      />
    </div>
  );
};
