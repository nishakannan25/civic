import React from 'react';
import { ShieldCheck, Lock, Eye, Key } from 'lucide-react';
import { AuditLogEntry } from '../types';

interface AuditLogTableProps {
  logs: AuditLogEntry[];
  isLoading: boolean;
  onSelectLog: (log: AuditLogEntry) => void;
}

export const AuditLogTable: React.FC<AuditLogTableProps> = ({
  logs,
  isLoading,
  onSelectLog,
}) => {
  if (isLoading) {
    return (
      <div className="rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-6 space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800/50 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs md:text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[11px] font-bold">
            <tr>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">Actor</th>
              <th className="py-3 px-4">Application</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4">Previous Hash</th>
              <th className="py-3 px-4">Entry Hash</th>
              <th className="py-3 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 font-mono text-xs">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                <td className="py-3.5 px-4 text-slate-400 text-[11px] whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-3.5 px-4 font-bold text-amber-500">{log.eventType}</td>
                <td className="py-3.5 px-4 font-sans text-slate-900 dark:text-slate-100 font-medium">
                  {log.actor}
                </td>
                <td className="py-3.5 px-4 text-blue-500 font-bold">{log.applicationId || 'N/A'}</td>
                <td className="py-3.5 px-4 font-sans text-slate-600 dark:text-slate-300 max-w-xs line-clamp-1">
                  {log.description}
                </td>
                <td className="py-3.5 px-4 text-slate-500 text-[10px] truncate max-w-[90px]">
                  {log.previousHash.substring(0, 12)}...
                </td>
                <td className="py-3.5 px-4 text-emerald-500 font-bold text-[10px] truncate max-w-[90px]">
                  {log.entryHash.substring(0, 12)}...
                </td>
                <td className="py-3.5 px-4 text-right font-sans">
                  <button
                    onClick={() => onSelectLog(log)}
                    className="px-2 py-1 rounded border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-[11px] font-semibold text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-1 ml-auto"
                  >
                    <Eye className="w-3 h-3 text-blue-500" />
                    <span>Payload</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
