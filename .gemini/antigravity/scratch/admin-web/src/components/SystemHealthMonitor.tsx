import React from 'react';
import { Server, Database, Cpu, Wifi, RefreshCw, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { SystemHealth, SystemServiceStatus } from '../types';

interface SystemHealthProps {
  health?: SystemHealth;
  isLoading: boolean;
  onRefresh?: () => void;
}

export const SystemHealthMonitor: React.FC<SystemHealthProps> = ({ health, isLoading, onRefresh }) => {
  const getBadge = (status?: SystemServiceStatus) => {
    switch (status) {
      case 'Connected':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Connected
          </span>
        );
      case 'Checking':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Checking...
          </span>
        );
      case 'Unavailable':
      default:
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
            <XCircle className="w-3.5 h-3.5 mr-1" /> Unavailable
          </span>
        );
    }
  };

  const services = [
    { name: 'Backend API', detail: 'http://localhost:8000', icon: Server, status: health?.backend },
    { name: 'SQLite DB', detail: 'Primary store (Local)', icon: Database, status: health?.sqlite },
    { name: 'Redis Cache', detail: 'Port 6379 (Task Queue)', icon: Cpu, status: health?.redis },
    { name: 'WebSocket Stream', detail: 'Real-time VeriFlow feed', icon: Wifi, status: health?.websocket },
  ];

  return (
    <div className="rounded-xl border p-5 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs">
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-base tracking-tight flex items-center">
            <Server className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
            System Health & Operations
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Real-time infrastructure probes and connection states
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-500' : ''}`} />
            <span>Refresh Probes</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        {services.map((svc, idx) => {
          const Icon = svc.icon;
          return (
            <div
              key={idx}
              className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center">
                  <Icon className="w-3.5 h-3.5 mr-1 text-blue-500" /> {svc.name}
                </span>
                {getBadge(svc.status)}
              </div>
              <div className="text-xs font-medium text-slate-900 dark:text-slate-200 truncate">
                {svc.detail}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
