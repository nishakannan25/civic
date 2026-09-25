import React from 'react';
import { useDashboardStats, useDashboardActivities, useSystemHealth } from '../hooks/useDashboard';
import { DashboardSummaryCards } from '../components/DashboardSummaryCards';
import { SystemHealthMonitor } from '../components/SystemHealthMonitor';
import { RecentActivityStream } from '../components/RecentActivityStream';
import { DashboardQuickActions } from '../components/DashboardQuickActions';
import { AlertCircle } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: statsLoading, isError: statsError, refetch: refetchStats } = useDashboardStats();
  const { data: activities, isLoading: activitiesLoading, isError: activitiesError } = useDashboardActivities();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useSystemHealth();

  return (
    <div className="space-y-6 pb-8">
      {/* Overview Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight">System Operational Overview</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time scholarship management, VeriFlow rule engine metrics, and active policy states
          </p>
        </div>

        {/* Live Broadcast Trigger to Applicant Web */}
        <button
          type="button"
          onClick={async () => {
            try {
              const backendHost = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
              await fetch(`${backendHost}/api/admin/scholarships/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  scholarshipId: 'SCH-TN-2026',
                  title: 'National Merit STEM Fellowship 2026',
                  oldAmount: '₹1,50,000',
                  newAmount: '₹2,00,000',
                  targetUrl: '/scholarships',
                }),
              });
              alert('📢 Real-time update broadcasted! Check the Applicant Portal tab for the live pop-up toast!');
            } catch (err) {
              alert('Broadcast failed: Check backend connection.');
            }
          }}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-md transition-all flex items-center space-x-2 shrink-0 animate-pulse"
        >
          <span>📢 Broadcast Real-Time Update to Applicants</span>
        </button>
      </div>

      {/* API Error Alert */}
      {(statsError || activitiesError) && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between text-xs text-amber-600 dark:text-amber-400">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-amber-500" />
            <span>FastAPI Backend offline/standby — Displaying dev environment cached operational states.</span>
          </div>
          <button
            onClick={() => refetchStats()}
            className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 font-semibold text-amber-800 dark:text-amber-300"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* 1. Summary Cards */}
      <DashboardSummaryCards stats={stats} isLoading={statsLoading} />

      {/* 2. Quick Actions Shortcuts */}
      <DashboardQuickActions />

      {/* 3. System Health Monitor */}
      <SystemHealthMonitor health={health} isLoading={healthLoading} onRefresh={() => refetchHealth()} />

      {/* 4. Recent Activity Stream */}
      <RecentActivityStream activities={activities} isLoading={activitiesLoading} />
    </div>
  );
};
