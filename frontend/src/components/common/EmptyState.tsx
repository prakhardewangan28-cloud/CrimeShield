import React, { type ReactNode } from 'react';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-dashed border-[#1E293B] bg-[#0D1422]/50">
      <div className="p-4 rounded-2xl bg-[#111C2D] border border-[#1E293B] text-cyan-400 mb-4 shadow-inner">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-[#F1F5F9]">{title}</h3>
      <p className="text-sm text-[#94A3B8] max-w-sm mt-1 mb-6 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-5 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-sm transition-all duration-200 shadow-lg shadow-cyan-500/20 active:scale-95"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
