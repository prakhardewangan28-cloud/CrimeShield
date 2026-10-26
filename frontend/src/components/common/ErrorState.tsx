import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load data',
  message,
  onRetry
}) => {
  return (
    <div className="rounded-xl border border-rose-900/40 bg-rose-950/20 p-6 text-center">
      <div className="mx-auto w-12 h-12 rounded-full bg-rose-900/30 flex items-center justify-center text-rose-400 mb-3 border border-rose-800/40">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h4 className="text-base font-bold text-[#F1F5F9] mb-1">{title}</h4>
      <p className="text-xs text-rose-300/90 max-w-md mx-auto mb-4 font-mono">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#111C2D] border border-rose-800/40 text-xs font-semibold text-rose-300 hover:bg-rose-900/30 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
};
