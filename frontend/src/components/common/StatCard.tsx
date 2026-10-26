import React, { type ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: number | string;
  subtext?: string;
  icon: ReactNode;
  color?: 'cyan' | 'blue' | 'violet' | 'emerald' | 'amber' | 'rose';
  trend?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon,
  color = 'cyan',
  trend,
  onClick
}) => {
  const colorMap = {
    cyan: {
      border: 'hover:border-cyan-500/50 hover:shadow-glow-cyan',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      accent: 'text-cyan-400'
    },
    blue: {
      border: 'hover:border-blue-500/50 hover:shadow-glow-blue',
      iconBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      accent: 'text-blue-400'
    },
    violet: {
      border: 'hover:border-violet-500/50 hover:shadow-glow-violet',
      iconBg: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
      accent: 'text-violet-400'
    },
    emerald: {
      border: 'hover:border-emerald-500/50',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      accent: 'text-emerald-400'
    },
    amber: {
      border: 'hover:border-amber-500/50',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      accent: 'text-amber-400'
    },
    rose: {
      border: 'hover:border-rose-500/50',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      accent: 'text-rose-400'
    }
  };

  const scheme = colorMap[color] || colorMap.cyan;

  return (
    <div
      onClick={onClick}
      className={`relative bg-[#111C2D] border border-[#1E293B] rounded-xl p-5 transition-all duration-300 group ${
        onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''
      } ${scheme.border}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8] mb-1">
            {label}
          </p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#F1F5F9] font-mono tracking-tight">
              {value}
            </span>
            {trend && (
              <span className="text-xs font-medium text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/40">
                {trend}
              </span>
            )}
          </div>
          {subtext && (
            <p className="text-xs text-[#94A3B8] mt-2 line-clamp-1">
              {subtext}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg border ${scheme.iconBg} transition-transform group-hover:scale-110`}>
          {icon}
        </div>
      </div>
    </div>
  );
};
