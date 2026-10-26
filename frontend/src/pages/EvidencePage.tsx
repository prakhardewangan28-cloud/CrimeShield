import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  FileText,
  Plus,
  RefreshCw,
  Edit2,
  Trash2,
  Eye,
  Filter,
  User,
  Phone,
  MapPin,
  FolderOpen,
  Search,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { evidenceService } from '../services/evidenceService';
import { caseService } from '../services/caseService';
import { useBackendStatus } from '../context/BackendStatusContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { SearchBar } from '../components/common/SearchBar';
import { Modal } from '../components/common/Modal';
import { ConfirmationDialog } from '../components/common/ConfirmationDialog';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import type { Evidence, EvidenceProcessingStatus, Case, EvidenceCreatePayload } from '../types';

export const EvidencePage: React.FC = () => {
  const { addToast } = useBackendStatus();

  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [caseFilter, setCaseFilter] = useState<string>('all');

  // Modals & Panels
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editEvidence, setEditEvidence] = useState<Evidence | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Evidence | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [detailEvidence, setDetailEvidence] = useState<Evidence | null>(null);

  // Form State
  const [formData, setFormData] = useState<EvidenceCreatePayload>({
    evidence_code: '',
    case_id: 0,
    evidence_type: 'physical',
    description: '',
    location_reference: '',
    person_reference: '',
    phone_reference: '',
    processing_status: 'pending'
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load Data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [evRes, casesRes] = await Promise.all([
        evidenceService.getEvidence(),
        caseService.getCases()
      ]);
      setEvidenceList(evRes.evidence);
      setCases(casesRes.cases);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve evidence vault data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Lookup map: Case ID -> Case Code + Title
  const caseMap = useMemo(() => {
    const map = new Map<number, Case>();
    cases.forEach((c) => map.set(c.id, c));
    return map;
  }, [cases]);

  // Distinct evidence types from data
  const distinctTypes = useMemo(() => {
    const types = new Set<string>(['physical', 'digital', 'document', 'testimonial']);
    evidenceList.forEach((e) => types.add(e.evidence_type));
    return Array.from(types);
  }, [evidenceList]);

  // Filtered evidence
  const filteredEvidence = useMemo(() => {
    return evidenceList.filter((e) => {
      const matchesSearch =
        searchQuery === '' ||
        e.evidence_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (e.description && e.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (e.person_reference && e.person_reference.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (e.phone_reference && e.phone_reference.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (e.location_reference && e.location_reference.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesType = typeFilter === 'all' || e.evidence_type.toLowerCase() === typeFilter.toLowerCase();
      const matchesStatus = statusFilter === 'all' || e.processing_status === statusFilter;
      const matchesCase = caseFilter === 'all' || String(e.case_id) === caseFilter;

      return matchesSearch && matchesType && matchesStatus && matchesCase;
    });
  }, [evidenceList, searchQuery, typeFilter, statusFilter, caseFilter]);

  // Open Create Modal
  const handleOpenCreate = () => {
    const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
    setFormData({
      evidence_code: `EVD-${timestamp.slice(0, 8)}-${Math.floor(100 + Math.random() * 900)}`,
      case_id: cases.length > 0 ? cases[0].id : 0,
      evidence_type: 'physical',
      description: '',
      location_reference: '',
      person_reference: '',
      phone_reference: '',
      processing_status: 'pending'
    });
    setFormErrors({});
    setCreateModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEdit = (item: Evidence) => {
    setEditEvidence(item);
    setFormData({
      evidence_code: item.evidence_code,
      case_id: item.case_id,
      evidence_type: item.evidence_type,
      description: item.description || '',
      location_reference: item.location_reference || '',
      person_reference: item.person_reference || '',
      phone_reference: item.phone_reference || '',
      processing_status: item.processing_status
    });
    setFormErrors({});
  };

  // Validate
  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.evidence_code.trim()) errors.evidence_code = 'Evidence code is required';
    if (formData.evidence_code.length > 50) errors.evidence_code = 'Code must be <= 50 characters';
    if (!formData.case_id || formData.case_id <= 0) {
      errors.case_id = 'Please associate with a valid registered case';
    }
    if (!formData.evidence_type.trim()) errors.evidence_type = 'Evidence type is required';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Submit Create or Edit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      if (editEvidence) {
        await evidenceService.updateEvidence(editEvidence.id, formData);
        addToast('success', 'Evidence Updated', `Record ${formData.evidence_code} updated`);
        setEditEvidence(null);
      } else {
        await evidenceService.createEvidence(formData);
        addToast('success', 'Evidence Cataloged', `Record ${formData.evidence_code} added to Case #${formData.case_id}`);
        setCreateModalOpen(false);
      }
      await fetchData();
    } catch (err: unknown) {
      addToast('error', 'Operation Failed', err instanceof Error ? err.message : 'Could not save evidence');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Confirm Delete
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await evidenceService.deleteEvidence(deleteTarget.id);
      addToast('success', 'Evidence Removed', `Record ${deleteTarget.evidence_code} deleted`);
      setDeleteTarget(null);
      await fetchData();
    } catch (err: unknown) {
      addToast('error', 'Delete Failed', err instanceof Error ? err.message : 'Could not delete evidence');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#F1F5F9]">Evidence Vault & Chain of Custody</h2>
          <p className="text-xs text-[#94A3B8]">
            Forensic artifacts, witness testimony, communications, and relational correlation references.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 rounded-lg bg-[#111C2D] border border-[#1E293B] text-[#94A3B8] hover:text-white hover:border-cyan-500/40 transition-all"
            title="Refresh Evidence"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
          <button
            onClick={handleOpenCreate}
            disabled={cases.length === 0}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>Catalog New Evidence</span>
          </button>
        </div>
      </div>

      {/* Case Warning if No Cases Exist */}
      {cases.length === 0 && !loading && (
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/40 flex items-center justify-between text-xs text-amber-300">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>No cases exist yet. Evidence requires an associated case foreign key. Create a case first.</span>
          </div>
        </div>
      )}

      {/* Filters Bar */}
      <div className="p-4 rounded-xl bg-[#111C2D] border border-[#1E293B] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search by code, person, phone..."
        />

        {/* Evidence Type */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">All Evidence Types</option>
          {distinctTypes.map((t) => (
            <option key={t} value={t}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </option>
          ))}
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">All Processing Statuses</option>
          <option value="pending">Pending</option>
          <option value="processed">Processed</option>
          <option value="flagged">Flagged</option>
        </select>

        {/* Associated Case Filter */}
        <select
          value={caseFilter}
          onChange={(e) => setCaseFilter(e.target.value)}
          className="bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/50 truncate"
        >
          <option value="all">All Associated Cases</option>
          {cases.map((c) => (
            <option key={c.id} value={String(c.id)}>
              {c.case_code} — {c.title.slice(0, 25)}
            </option>
          ))}
        </select>
      </div>

      {/* Main Table */}
      {loading && evidenceList.length === 0 ? (
        <LoadingSkeleton rows={5} />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchData} />
      ) : filteredEvidence.length === 0 ? (
        <EmptyState
          icon={<FileText className="w-10 h-10" />}
          title="No Evidence Records Found"
          description={searchQuery || typeFilter !== 'all' ? 'Try adjusting your vault filters.' : 'Catalog your first piece of forensic evidence to begin cross-case intelligence analysis.'}
          actionLabel={cases.length > 0 ? 'Catalog Evidence' : undefined}
          onAction={cases.length > 0 ? handleOpenCreate : undefined}
        />
      ) : (
        <div className="bg-[#111C2D] border border-[#1E293B] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#0D1422] text-[#94A3B8] text-xs font-semibold uppercase tracking-wider border-b border-[#1E293B]">
                <tr>
                  <th className="py-3.5 px-4">Evidence Code</th>
                  <th className="py-3.5 px-4">Associated Case</th>
                  <th className="py-3.5 px-4">Type</th>
                  <th className="py-3.5 px-4">Description</th>
                  <th className="py-3.5 px-4">Matching References</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B] text-[#F1F5F9]">
                {filteredEvidence.map((ev) => {
                  const associatedCase = caseMap.get(ev.case_id);
                  return (
                    <tr key={ev.id} className="hover:bg-[#162338]/50 transition-colors group">
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/40 px-2 py-1 rounded border border-cyan-800/40">
                          {ev.evidence_code}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        {associatedCase ? (
                          <div>
                            <span className="font-mono text-xs font-semibold text-slate-300">
                              {associatedCase.case_code}
                            </span>
                            <div className="text-[11px] text-[#94A3B8] truncate max-w-[150px]">
                              {associatedCase.title}
                            </div>
                          </div>
                        ) : (
                          <span className="font-mono text-xs text-slate-500">Case #{ev.case_id}</span>
                        )}
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                          {ev.evidence_type}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 max-w-xs">
                        <div className="text-xs text-[#F1F5F9] truncate">
                          {ev.description || 'No description logged'}
                        </div>
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="flex flex-col gap-1 text-xs">
                          {ev.person_reference && (
                            <span className="inline-flex items-center gap-1 text-violet-300">
                              <User className="w-3 h-3 text-violet-400" />
                              <span className="font-medium">{ev.person_reference}</span>
                            </span>
                          )}
                          {ev.phone_reference && (
                            <span className="inline-flex items-center gap-1 text-emerald-300 font-mono text-[11px]">
                              <Phone className="w-3 h-3 text-emerald-400" />
                              <span>{ev.phone_reference}</span>
                            </span>
                          )}
                          {ev.location_reference && (
                            <span className="inline-flex items-center gap-1 text-cyan-300 font-mono text-[11px]">
                              <MapPin className="w-3 h-3 text-cyan-400" />
                              <span className="truncate max-w-[120px]">{ev.location_reference}</span>
                            </span>
                          )}
                          {!ev.person_reference && !ev.phone_reference && !ev.location_reference && (
                            <span className="text-slate-600 text-xs italic">No references</span>
                          )}
                        </div>
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <StatusBadge status={ev.processing_status} type="evidence" />
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => setDetailEvidence(ev)}
                            title="Inspect Evidence Details"
                            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-cyan-400 hover:bg-[#0D1422] transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleOpenEdit(ev)}
                            title="Edit Evidence"
                            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-blue-400 hover:bg-[#0D1422] transition-colors"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(ev)}
                            title="Expunge Evidence"
                            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-rose-400 hover:bg-[#0D1422] transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 border-t border-[#1E293B] bg-[#0D1422] text-xs text-[#94A3B8] flex items-center justify-between">
            <span>Showing {filteredEvidence.length} of {evidenceList.length} evidence items</span>
            <span className="font-mono">SQLite evidence table</span>
          </div>
        </div>
      )}

      {/* Inspect Evidence Modal */}
      {detailEvidence && (
        <Modal
          isOpen={!!detailEvidence}
          onClose={() => setDetailEvidence(null)}
          title={`Evidence File: ${detailEvidence.evidence_code}`}
          subtitle={`Forensic ID #${detailEvidence.id}`}
          maxWidth="lg"
        >
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                  {detailEvidence.evidence_type} Evidence
                </span>
                <StatusBadge status={detailEvidence.processing_status} type="evidence" size="md" />
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500">Forensic Description</span>
                <p className="text-xs text-[#F1F5F9] mt-0.5 leading-relaxed">
                  {detailEvidence.description || 'No description specified'}
                </p>
              </div>

              <div className="p-3 rounded-lg bg-[#111C2D] border border-[#1E293B] space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-cyan-400">
                  Extracted Matching References
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Person / Suspect:</span>
                    <span className="font-semibold text-violet-300">{detailEvidence.person_reference || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Phone Number:</span>
                    <span className="font-mono text-emerald-300">{detailEvidence.phone_reference || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Location / Geo:</span>
                    <span className="font-mono text-cyan-300 truncate block">{detailEvidence.location_reference || 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-[#94A3B8] pt-2 border-t border-[#1E293B]">
                <span>Associated Case: <strong>#{detailEvidence.case_id} ({caseMap.get(detailEvidence.case_id)?.case_code || 'Unknown'})</strong></span>
                <span className="font-mono">{detailEvidence.created_at?.slice(0, 19) || '—'}</span>
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* Add / Edit Evidence Modal */}
      <Modal
        isOpen={createModalOpen || !!editEvidence}
        onClose={() => {
          setCreateModalOpen(false);
          setEditEvidence(null);
        }}
        title={editEvidence ? `Edit Evidence: ${editEvidence.evidence_code}` : 'Catalog New Evidence Item'}
        subtitle="Associate physical, digital, or testimonial artifacts with an investigation dossier."
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Associated Case Selector */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Associated Case <span className="text-rose-400">*</span>
            </label>
            <select
              value={formData.case_id}
              onChange={(e) => setFormData({ ...formData, case_id: Number(e.target.value) })}
              className={`w-full bg-[#0D1422] border rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none ${
                formErrors.case_id ? 'border-rose-500' : 'border-[#1E293B] focus:border-cyan-500/60'
              }`}
            >
              {cases.length === 0 ? (
                <option value={0}>No cases available — create a case first</option>
              ) : (
                cases.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.case_code} — {c.title}
                  </option>
                ))
              )}
            </select>
            {formErrors.case_id && (
              <p className="text-xs text-rose-400 mt-1">{formErrors.case_id}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Evidence Code */}
            <div>
              <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
                Evidence Code <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={formData.evidence_code}
                onChange={(e) => setFormData({ ...formData, evidence_code: e.target.value })}
                placeholder="e.g. EVD-2026-001"
                maxLength={50}
                className={`w-full bg-[#0D1422] border rounded-lg px-3 py-2 text-sm text-[#F1F5F9] font-mono focus:outline-none ${
                  formErrors.evidence_code ? 'border-rose-500' : 'border-[#1E293B] focus:border-cyan-500/60'
                }`}
              />
              {formErrors.evidence_code && (
                <p className="text-xs text-rose-400 mt-1">{formErrors.evidence_code}</p>
              )}
            </div>

            {/* Evidence Type */}
            <div>
              <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
                Evidence Type <span className="text-rose-400">*</span>
              </label>
              <select
                value={formData.evidence_type}
                onChange={(e) => setFormData({ ...formData, evidence_type: e.target.value })}
                className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
              >
                <option value="physical">Physical Artifact</option>
                <option value="digital">Digital Data / Disk</option>
                <option value="document">Document / Record</option>
                <option value="testimonial">Witness Testimony</option>
                <option value="biometric">Biometric Sample</option>
                <option value="telecom">Telecommunications Record</option>
              </select>
            </div>
          </div>

          {/* Forensic Reference Inputs */}
          <div className="p-3.5 rounded-xl bg-[#0D1422] border border-[#1E293B] space-y-3">
            <span className="text-xs font-bold text-cyan-400 block">
              Forensic Network Identifiers (Used for Automated Matching)
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Person Reference */}
              <div>
                <label className="block text-[11px] font-semibold text-[#94A3B8] mb-1">
                  Person Reference
                </label>
                <input
                  type="text"
                  value={formData.person_reference || ''}
                  onChange={(e) => setFormData({ ...formData, person_reference: e.target.value })}
                  placeholder="e.g. John Doe"
                  className="w-full bg-[#111C2D] border border-[#1E293B] rounded-lg px-2.5 py-1.5 text-xs text-[#F1F5F9] focus:outline-none focus:border-violet-500/60"
                />
              </div>

              {/* Phone Reference */}
              <div>
                <label className="block text-[11px] font-semibold text-[#94A3B8] mb-1">
                  Phone Reference
                </label>
                <input
                  type="text"
                  value={formData.phone_reference || ''}
                  onChange={(e) => setFormData({ ...formData, phone_reference: e.target.value })}
                  placeholder="e.g. +1-555-0199"
                  className="w-full bg-[#111C2D] border border-[#1E293B] rounded-lg px-2.5 py-1.5 text-xs text-[#F1F5F9] font-mono focus:outline-none focus:border-emerald-500/60"
                />
              </div>

              {/* Location Reference */}
              <div>
                <label className="block text-[11px] font-semibold text-[#94A3B8] mb-1">
                  Location / Geo Ref
                </label>
                <input
                  type="text"
                  value={formData.location_reference || ''}
                  onChange={(e) => setFormData({ ...formData, location_reference: e.target.value })}
                  placeholder="e.g. 40.7589,-73.9851"
                  className="w-full bg-[#111C2D] border border-[#1E293B] rounded-lg px-2.5 py-1.5 text-xs text-[#F1F5F9] font-mono focus:outline-none focus:border-cyan-500/60"
                />
              </div>
            </div>
            <p className="text-[10px] text-[#64748B]">
              CRIMESHIELD matches cases when two pieces of evidence share matching persons, phone numbers, or locations within 50km.
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Description / Notes
            </label>
            <textarea
              rows={2}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Chain of custody logs, recovery location, handling officer..."
              className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
            />
          </div>

          {/* Processing Status */}
          <div>
            <label className="block text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1.5">
              Processing Status
            </label>
            <select
              value={formData.processing_status}
              onChange={(e) => setFormData({ ...formData, processing_status: e.target.value as EvidenceProcessingStatus })}
              className="w-full bg-[#0D1422] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-[#F1F5F9] focus:outline-none focus:border-cyan-500/60"
            >
              <option value="pending">Pending Forensic Analysis</option>
              <option value="processed">Processed & Verified</option>
              <option value="flagged">Flagged for Secondary Review</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-[#1E293B]">
            <button
              type="button"
              onClick={() => {
                setCreateModalOpen(false);
                setEditEvidence(null);
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
              {isSubmitting ? 'Cataloging...' : editEvidence ? 'Update Evidence' : 'Store Evidence'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmationDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Expunge Evidence Artifact"
        message={`Are you sure you want to permanently delete evidence "${deleteTarget?.evidence_code}"? Any connection leads relying on this evidence will be affected.`}
        confirmText="Expunge Record"
        isDanger={true}
        isLoading={isDeleting}
      />
    </div>
  );
};
