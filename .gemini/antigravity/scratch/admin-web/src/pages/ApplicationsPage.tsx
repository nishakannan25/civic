import React, { useState } from 'react';
import { Layers, Search, ShieldCheck } from 'lucide-react';
import { useApplications } from '../hooks/useApplications';
import { ApplicationMonitorItem } from '../types';
import { ApplicationListTable } from '../components/ApplicationListTable';
import { ApplicationDetailsModal } from '../components/ApplicationDetailsModal';

import { useAdminWebSocket } from '../hooks/useAdminWebSocket';

export const ApplicationsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const { data: initialApps = [], isLoading } = useApplications(search);
  const realtimeApps = useAdminWebSocket();
  const [selectedApp, setSelectedApp] = useState<ApplicationMonitorItem | null>(null);

  // Merge real-time WebSocket registrations with existing application monitor data
  const applications = [...realtimeApps, ...initialApps];

  return (
    <div className="space-y-6 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center">
            <Layers className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
            Active Application Monitor
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Realtime applicant application monitoring, active field locks & VeriFlow status tracking
          </p>
        </div>
      </div>

      {/* Governance Banner */}
      <div className="p-4 rounded-xl bg-slate-900 text-white border border-slate-800 flex items-start space-x-3 shadow-md">
        <ShieldCheck className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed space-y-1">
          <div className="font-bold text-slate-100">
            Read-Only Applicant Governance Protocol:
          </div>
          <p className="text-slate-300">
            Admins are strictly <span className="text-amber-400 font-semibold">PROHIBITED from arbitrarily editing</span> applicant application data. Inspection is strictly read-only for rule compliance verification.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="p-4 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by application number, applicant name, or scholarship..."
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 pl-9 pr-4 text-xs md:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Table */}
      <ApplicationListTable
        applications={applications}
        isLoading={isLoading}
        onSelectApplication={(app) => setSelectedApp(app)}
      />

      {/* Details Modal */}
      <ApplicationDetailsModal
        application={selectedApp}
        onClose={() => setSelectedApp(null)}
      />
    </div>
  );
};
