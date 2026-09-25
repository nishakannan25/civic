import React from 'react';
import { X, Sparkles, AlertTriangle, ShieldCheck, UserCheck, Calendar } from 'lucide-react';
import { VeriflowEvent } from '../types';

interface VeriflowEventDetailsModalProps {
  event: VeriflowEvent | null;
  onClose: () => void;
}

export const VeriflowEventDetailsModal: React.FC<VeriflowEventDetailsModalProps> = ({
  event,
  onClose,
}) => {
  if (!event) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-amber-500 font-bold uppercase tracking-wider">
              {event.id} • {event.classification.toUpperCase()} IMPACT
            </span>
            <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 mt-0.5">
              VeriFlow Event Execution Details
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Scholarship: <strong className="text-slate-800 dark:text-slate-200">{event.scholarshipTitle}</strong>
            </p>
          </div>

          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* AI Explanation Box */}
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-1 text-xs">
          <div className="font-bold text-amber-700 dark:text-amber-400 flex items-center">
            <Sparkles className="w-4 h-4 mr-1.5" /> VeriFlow AI Evaluation Explanation:
          </div>
          <p className="text-amber-950 dark:text-amber-200 leading-relaxed font-medium">
            "{event.aiExplanation}"
          </p>
        </div>

        {/* Side-by-Side Old vs New Value Diff */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 space-y-1 text-xs">
            <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
              OLD VALUE (v{event.oldVersion})
            </span>
            <div className="font-semibold text-slate-800 dark:text-slate-200 font-mono">
              {event.oldValue}
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-1 text-xs">
            <span className="text-[10px] font-mono font-bold text-blue-500 uppercase tracking-wider">
              NEW VALUE (v{event.newVersion})
            </span>
            <div className="font-semibold text-blue-950 dark:text-blue-200 font-mono">
              {event.newValue}
            </div>
          </div>
        </div>

        {/* Recovery Decisions Stream */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Applicant Recovery Decisions ({event.recoveryDecisions.length})
          </h4>

          {event.recoveryDecisions.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
              No applicant recovery decisions required for this change classification.
            </div>
          ) : (
            <div className="space-y-2">
              {event.recoveryDecisions.map((dec) => (
                <div
                  key={dec.id}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-xs flex items-center justify-between"
                >
                  <div>
                    <div className="font-bold text-slate-900 dark:text-slate-100">
                      {dec.applicantName}{' '}
                      <span className="font-mono text-[10px] text-slate-400">({dec.applicationNumber})</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      Decision: <strong className="text-blue-500">{dec.decision}</strong>
                    </div>
                  </div>

                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                    {dec.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
};
