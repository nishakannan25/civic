import React from 'react';
import { Eye, ShieldAlert, CheckCircle, Clock, AlertTriangle, HelpCircle } from 'lucide-react';
import { VeriflowEvent, VeriflowClassification, VeriflowStatus } from '../types';

interface VeriflowEventsTableProps {
  events: VeriflowEvent[];
  isLoading: boolean;
  onSelectEvent: (event: VeriflowEvent) => void;
}

export const VeriflowEventsTable: React.FC<VeriflowEventsTableProps> = ({
  events,
  isLoading,
  onSelectEvent,
}) => {
  const getClassificationBadge = (cls: VeriflowClassification) => {
    switch (cls) {
      case 'blocking':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
            Blocking
          </span>
        );
      case 'informational':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            Informational
          </span>
        );
      case 'cosmetic':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/10 text-slate-600 dark:text-slate-300 border border-slate-500/20">
            Cosmetic
          </span>
        );
    }
  };

  const getStatusBadge = (st: VeriflowStatus) => {
    switch (st) {
      case 'resolved':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center w-fit">
            <CheckCircle className="w-3 h-3 mr-1 text-emerald-500" /> Resolved
          </span>
        );
      case 'notified':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center w-fit">
            <Clock className="w-3 h-3 mr-1 text-blue-500" /> Notified
          </span>
        );
      case 'contested':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-red-500/10 text-red-600 dark:text-red-400 flex items-center w-fit">
            <AlertTriangle className="w-3 h-3 mr-1 text-red-500" /> Contested
          </span>
        );
      case 'grace_period_requested':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center w-fit">
            <Clock className="w-3 h-3 mr-1 text-purple-500" /> Grace Requested
          </span>
        );
      case 'classified':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center w-fit">
            Classified
          </span>
        );
      case 'detected':
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-500/10 text-slate-500 flex items-center w-fit">
            Detected
          </span>
        );
    }
  };

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
              <th className="py-3 px-4">Change ID & Scholarship</th>
              <th className="py-3 px-4">Fact Key</th>
              <th className="py-3 px-4">Versions</th>
              <th className="py-3 px-4">Classification</th>
              <th className="py-3 px-4">Affected Field</th>
              <th className="py-3 px-4">Affected Apps</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Created At</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {events.map((evt) => (
              <tr key={evt.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                {/* Change ID & Scholarship */}
                <td className="py-3.5 px-4">
                  <div className="font-bold text-slate-900 dark:text-slate-100 line-clamp-1">
                    {evt.scholarshipTitle}
                  </div>
                  <div className="text-xs font-mono text-blue-500 font-semibold mt-0.5">
                    {evt.id}
                  </div>
                </td>

                {/* Fact Key */}
                <td className="py-3.5 px-4 font-mono text-xs text-slate-600 dark:text-slate-300">
                  {evt.factKey}
                </td>

                {/* Versions */}
                <td className="py-3.5 px-4 font-mono text-xs text-slate-500">
                  v{evt.oldVersion} → <span className="font-bold text-blue-600 dark:text-blue-400">v{evt.newVersion}</span>
                </td>

                {/* Classification */}
                <td className="py-3.5 px-4">{getClassificationBadge(evt.classification)}</td>

                {/* Affected Field */}
                <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 text-xs font-mono">
                  {evt.affectedField}
                </td>

                {/* Affected Apps Count */}
                <td className="py-3.5 px-4 font-bold text-amber-600 dark:text-amber-400">
                  {evt.affectedApplicationsCount} Applications
                </td>

                {/* Status */}
                <td className="py-3.5 px-4">{getStatusBadge(evt.status)}</td>

                {/* Created At */}
                <td className="py-3.5 px-4 text-slate-400 text-xs">
                  {new Date(evt.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </td>

                {/* Actions */}
                <td className="py-3.5 px-4 text-right">
                  <button
                    onClick={() => onSelectEvent(evt)}
                    className="px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-1 ml-auto"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-500" />
                    <span>Details</span>
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
