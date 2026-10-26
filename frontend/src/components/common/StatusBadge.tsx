import React from 'react';
import type { CaseStatus, EvidenceProcessingStatus, ConnectionReviewStatus } from '../../types';

interface StatusBadgeProps {
  status: CaseStatus | EvidenceProcessingStatus | ConnectionReviewStatus | string;
  type?: 'case' | 'evidence' | 'connection' | 'type';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'case', size = 'sm' }) => {
  const normalized = (status || '').toLowerCase().replace(/\s+/g, '_');

  let bg = 'bg-slate-800/80 text-slate-300 border-slate-700';
  let dot = 'bg-slate-400';
  let label = status;

  // Case statuses
  if (normalized === 'open') {
    bg = 'bg-cyan-950/60 text-cyan-300 border-cyan-800/60 shadow-[0_0_10px_-2px_rgba(34,211,238,0.2)]';
    dot = 'bg-cyan-400';
    label = 'Open';
  } else if (normalized === 'under_review') {
    bg = 'bg-amber-950/60 text-amber-300 border-amber-800/60 shadow-[0_0_10px_-2px_rgba(245,158,11,0.2)]';
    dot = 'bg-amber-400 animate-pulse';
    label = 'Under Review';
  } else if (normalized === 'closed') {
    bg = 'bg-slate-900/80 text-slate-400 border-slate-800';
    dot = 'bg-slate-500';
    label = 'Closed';
  }

  // Evidence statuses
  else if (normalized === 'pending') {
    bg = 'bg-amber-950/60 text-amber-300 border-amber-800/60';
    dot = 'bg-amber-400';
    label = 'Pending';
  } else if (normalized === 'processed') {
    bg = 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60';
    dot = 'bg-emerald-400';
    label = 'Processed';
  } else if (normalized === 'flagged') {
    bg = 'bg-rose-950/60 text-rose-300 border-rose-800/60';
    dot = 'bg-rose-400';
    label = 'Flagged';
  }

  // Connection review statuses
  else if (normalized === 'confirmed_for_review') {
    bg = 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60 shadow-[0_0_10px_-2px_rgba(34,197,94,0.25)]';
    dot = 'bg-emerald-400';
    label = 'Confirmed for Review';
  } else if (normalized === 'dismissed') {
    bg = 'bg-slate-900/80 text-slate-400 border-slate-800';
    dot = 'bg-slate-500';
    label = 'Dismissed';
  }

  // Connection types
  else if (normalized.includes('person')) {
    bg = 'bg-violet-950/60 text-violet-300 border-violet-800/60';
    dot = 'bg-violet-400';
    label = 'Person Match';
  } else if (normalized.includes('location')) {
    bg = 'bg-cyan-950/60 text-cyan-300 border-cyan-800/60';
    dot = 'bg-cyan-400';
    label = 'Location Match';
  } else if (normalized.includes('phone')) {
    bg = 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60';
    dot = 'bg-emerald-400';
    label = 'Phone Match';
  }

  const sizeClasses = size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${bg} ${sizeClasses} whitespace-nowrap`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
};
