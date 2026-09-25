import React from 'react';
import { X, Key, ShieldCheck, Code } from 'lucide-react';
import { AuditLogEntry } from '../types';

interface AuditDetailsModalProps {
  log: AuditLogEntry | null;
  onClose: () => void;
}

export const AuditDetailsModal: React.FC<AuditDetailsModalProps> = ({ log, onClose }) => {
  if (!log) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-xl w-full shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-emerald-500 font-bold uppercase tracking-wider">
              {log.id} • READ-ONLY AUDIT PAYLOAD
            </span>
            <h3 className="font-bold text-base text-slate-900 dark:text-slate-100 mt-0.5">
              {log.eventType}
            </h3>
          </div>

          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Hashes Box */}
        <div className="p-3.5 rounded-xl bg-slate-900 text-white border border-slate-800 space-y-2 font-mono text-[11px]">
          <div>
            <span className="text-slate-500 uppercase text-[9px] font-bold tracking-wider">PREVIOUS HASH:</span>
            <div className="text-slate-300 break-all">{log.previousHash}</div>
          </div>
          <div>
            <span className="text-emerald-400 uppercase text-[9px] font-bold tracking-wider">ENTRY HASH:</span>
            <div className="text-emerald-300 font-bold break-all">{log.entryHash}</div>
          </div>
        </div>

        {/* JSON Payload */}
        <div className="space-y-1">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center">
            <Code className="w-3.5 h-3.5 mr-1" /> Payload JSON:
          </div>
          <pre className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-xs text-slate-800 dark:text-slate-200 overflow-x-auto">
            {JSON.stringify(log.payload, null, 2)}
          </pre>
        </div>

        <div className="flex justify-end pt-2 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
          >
            Close Audit Entry
          </button>
        </div>
      </div>
    </div>
  );
};
