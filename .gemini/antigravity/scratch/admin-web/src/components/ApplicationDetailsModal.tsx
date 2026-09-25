import React from 'react';
import { X, ShieldAlert, Lock, User, FileText, Sparkles, AlertCircle } from 'lucide-react';
import { ApplicationMonitorItem } from '../types';

interface ApplicationDetailsModalProps {
  application: ApplicationMonitorItem | null;
  onClose: () => void;
}

export const ApplicationDetailsModal: React.FC<ApplicationDetailsModalProps> = ({
  application,
  onClose,
}) => {
  if (!application) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-blue-500 font-bold uppercase tracking-wider">
              {application.applicationNumber} • READ-ONLY AUDIT VIEW
            </span>
            <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 mt-0.5 flex items-center">
              Application Inspection Snapshot
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Scholarship: <strong className="text-slate-800 dark:text-slate-200">{application.scholarshipTitle}</strong>
            </p>
          </div>

          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Governance Notice */}
        <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 text-xs flex items-center space-x-2 text-slate-600 dark:text-slate-300">
          <ShieldAlert className="w-4 h-4 text-blue-500 shrink-0" />
          <span>
            Strict Data Policy: Admins must <strong>NOT arbitrarily edit</strong> applicant submission data.
          </span>
        </div>

        {/* Applicant Information */}
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2 text-xs">
          <div className="font-bold text-slate-900 dark:text-slate-100 flex items-center">
            <User className="w-3.5 h-3.5 mr-1.5 text-blue-500" /> Permitted Applicant Profile:
          </div>
          <div className="grid grid-cols-2 gap-2 text-slate-600 dark:text-slate-300">
            <div>
              Applicant ID: <strong className="text-slate-800 dark:text-slate-200 font-mono">{application.applicantId}</strong>
            </div>
            <div>
              Name: <strong className="text-slate-800 dark:text-slate-200">{application.applicantName}</strong>
            </div>
            <div>
              Email: <strong className="text-slate-800 dark:text-slate-200">{application.email}</strong>
            </div>
            <div>
              Fact Snapshot: <strong className="text-blue-500 font-mono">v{application.currentFactSnapshotVersion}</strong>
            </div>
          </div>
        </div>

        {/* Active Field Locks */}
        {application.activeFieldLocks.length > 0 && (
          <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs space-y-1">
            <div className="font-bold text-red-600 dark:text-red-400 flex items-center">
              <Lock className="w-4 h-4 mr-1.5" /> VeriFlow Active Field Locks:
            </div>
            <p className="text-red-950 dark:text-red-200">
              Field <code className="font-mono font-bold bg-red-900/20 px-1 py-0.5 rounded">{application.activeFieldLocks.join(', ')}</code> is locked due to an unaddressed policy rule change.
            </p>
          </div>
        )}

        {/* Recovery Decisions Stream */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Recovery Decisions ({application.recoveryDecisions.length})
          </h4>

          {application.recoveryDecisions.length === 0 ? (
            <div className="p-3 text-center text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
              No active recovery decisions pending for this application.
            </div>
          ) : (
            application.recoveryDecisions.map((dec) => (
              <div
                key={dec.id}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-xs flex items-center justify-between"
              >
                <div>
                  <div className="font-bold text-slate-900 dark:text-slate-100">{dec.decision}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    Submitted: {new Date(dec.timestamp).toLocaleString()}
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                  {dec.status}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
          >
            Close Snapshot
          </button>
        </div>
      </div>
    </div>
  );
};
