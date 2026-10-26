import React, { useState } from 'react';
import { Presentation, ChevronDown, ChevronUp, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DemoModeBanner: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const steps = [
    {
      num: 1,
      title: 'Inspect Dashboard',
      desc: 'Check live metrics, case status distribution, and API health.',
      link: '/'
    },
    {
      num: 2,
      title: 'Create Fictional Cases',
      desc: 'Add Case 1 and Case 2 in Case Management.',
      link: '/cases'
    },
    {
      num: 3,
      title: 'Attach Fragmented Evidence',
      desc: 'Link evidence records with shared location/person/phone.',
      link: '/evidence'
    },
    {
      num: 4,
      title: 'Run Network Analysis',
      desc: 'Trigger backend analysis algorithm to detect cross-case links.',
      link: '/network'
    },
    {
      num: 5,
      title: 'Review Connections',
      desc: 'Confirm lead or dismiss with analyst notes via PATCH.',
      link: '/connections'
    },
    {
      num: 6,
      title: 'Export Official Report',
      desc: 'Download case intelligence as CSV or plain text report.',
      link: '/reports'
    }
  ];

  return (
    <div className="mb-6 rounded-xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/40 via-[#111C2D] to-violet-950/30 overflow-hidden shadow-lg">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between px-5 py-3 cursor-pointer select-none hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <Presentation className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-[#F1F5F9]">College Viva & Demonstration Mode</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> Live Demo Guide
              </span>
            </div>
            <p className="text-xs text-[#94A3B8]">
              Follow this 6-step workflow to showcase CRIMESHIELD during your project evaluation.
            </p>
          </div>
        </div>
        <button className="text-[#94A3B8] hover:text-white p-1 rounded-lg">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isOpen && (
        <div className="px-5 pb-5 pt-2 border-t border-[#1E293B] bg-[#0D1422]/70">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
            {steps.map((s) => (
              <Link
                key={s.num}
                to={s.link}
                className="group flex items-start gap-3 p-3 rounded-lg bg-[#111C2D] border border-[#1E293B] hover:border-cyan-500/40 hover:bg-[#162338] transition-all"
              >
                <div className="w-6 h-6 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                  {s.num}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h6 className="text-xs font-bold text-[#F1F5F9] group-hover:text-cyan-300 transition-colors">
                      {s.title}
                    </h6>
                    <ArrowRight className="w-3 h-3 text-[#94A3B8] group-hover:text-cyan-300 group-hover:translate-x-0.5 transition-all" />
                  </div>
                  <p className="text-[11px] text-[#94A3B8] mt-0.5 leading-snug">
                    {s.desc}
                  </p>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-4 p-2.5 rounded-lg bg-amber-950/20 border border-amber-900/30 text-[11px] text-amber-300/90 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>
              <strong>Investigative Ethics Notice:</strong> All data is fictional simulation for academic purposes. Potential connections are leads requiring human review, not automated conviction.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
