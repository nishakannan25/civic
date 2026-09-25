import React from 'react';
import { Eye, ShieldAlert, Lock, AlertTriangle } from 'lucide-react';
import { ApplicationMonitorItem, ApplicationStatus } from '../types';

interface ApplicationListTableProps {
  applications: ApplicationMonitorItem[];
  isLoading: boolean;
  onSelectApplication: (app: ApplicationMonitorItem) => void;
}

export const ApplicationListTable: React.FC<ApplicationListTableProps> = ({
  applications,
  isLoading,
  onSelectApplication,
}) => {
  const getStatusBadge = (st: ApplicationStatus) => {
    switch (st) {
      case 'APPROVED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            APPROVED
          </span>
        );
      case 'ACTION_REQUIRED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20 flex items-center w-fit">
            <AlertTriangle className="w-3 h-3 mr-1 text-red-500" /> ACTION REQUIRED
          </span>
        );
      case 'UNDER_REVIEW':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
            UNDER REVIEW
          </span>
        );
      case 'REJECTED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-500/20">
            REJECTED
          </span>
        );
      case 'SUBMITTED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
            SUBMITTED
          </span>
        );
      case 'DRAFT':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/10 text-slate-500 border border-slate-500/20">
            DRAFT
          </span>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-6 space-y-4">
        {[...Array(3)].map((_, i) => (
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
              <th className="py-3 px-4">Application Number</th>
              <th className="py-3 px-4">Applicant Name</th>
              <th className="py-3 px-4">Scholarship</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Active Field Locks</th>
              <th className="py-3 px-4">VeriFlow Status</th>
              <th className="py-3 px-4">Last Updated</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {applications.map((app) => (
              <tr key={app.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                <td className="py-3.5 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">
                  {app.applicationNumber}
                </td>
                <td className="py-3.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                  {app.applicantName}
                  <div className="text-[11px] font-normal text-slate-400">{app.email}</div>
                </td>
                <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 font-medium line-clamp-1 max-w-[200px]">
                  {app.scholarshipTitle}
                </td>
                <td className="py-3.5 px-4">{getStatusBadge(app.status)}</td>
                <td className="py-3.5 px-4">
                  {app.activeFieldLocks.length > 0 ? (
                    <div className="flex items-center space-x-1 text-red-500 font-mono text-xs font-semibold">
                      <Lock className="w-3 h-3" />
                      <span>{app.activeFieldLocks.join(', ')}</span>
                    </div>
                  ) : (
                    <span className="text-slate-400 text-xs">None</span>
                  )}
                </td>
                <td className="py-3.5 px-4 uppercase text-[11px] font-mono font-bold text-amber-500">
                  {app.veriflowStatus}
                </td>
                <td className="py-3.5 px-4 text-slate-400 text-xs">
                  {new Date(app.updatedAt).toLocaleDateString()}
                </td>
                <td className="py-3.5 px-4 text-right">
                  <button
                    onClick={() => onSelectApplication(app)}
                    className="px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-1 ml-auto"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-500" />
                    <span>View</span>
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
