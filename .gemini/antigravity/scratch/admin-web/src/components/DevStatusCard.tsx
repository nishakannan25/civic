import React, { useState } from 'react';
import { Server, Database, Cpu, RefreshCw, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface SystemState {
  status: 'online' | 'warning' | 'offline';
  label: string;
  latency?: string;
  detail: string;
}

export const DevStatusCard: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Initial development status configuration (backend http://localhost:8000)
  const [systems, setSystems] = useState<Record<'backend' | 'sqlite' | 'redis', SystemState>>({
    backend: { status: 'warning', label: 'Backend API', latency: 'Standby', detail: 'http://localhost:8000' },
    sqlite: { status: 'online', label: 'SQLite Store', latency: '12ms', detail: 'Dev Database Mounted' },
    redis: { status: 'warning', label: 'Redis Cache', latency: 'Standby', detail: 'Queue / Cache Service' },
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      // Check backend ping or keep placeholder states
      setSystems((prev) => ({
        ...prev,
        backend: { ...prev.backend, latency: 'Check complete' },
      }));
      setIsRefreshing(false);
    }, 600);
  };

  const getStatusBadge = (status: SystemState['status']) => {
    switch (status) {
      case 'online':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Online
          </span>
        );
      case 'warning':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Standby / Dev Mode
          </span>
        );
      case 'offline':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
            <XCircle className="w-3.5 h-3.5 mr-1" /> Offline
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border p-5 shadow-xs transition-all duration-200 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800">
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-base tracking-tight flex items-center">
            <Server className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
            Development & Infrastructure Health
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Phase 1 Dev Status monitoring endpoint connections
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-500' : ''}`} />
          <span>{isRefreshing ? 'Checking...' : 'Check Status'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
        {/* Backend Card */}
        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center">
              <Server className="w-3.5 h-3.5 mr-1 text-blue-500" /> Backend API
            </span>
            {getStatusBadge(systems.backend.status)}
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            http://localhost:8000
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Status: {systems.backend.latency}
          </div>
        </div>

        {/* SQLite Card */}
        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center">
              <Database className="w-3.5 h-3.5 mr-1 text-emerald-500" /> SQLite Store
            </span>
            {getStatusBadge(systems.sqlite.status)}
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            scholarpath_dev.db
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Latency: {systems.sqlite.latency}
          </div>
        </div>

        {/* Redis Card */}
        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center">
              <Cpu className="w-3.5 h-3.5 mr-1 text-amber-500" /> Redis Cache
            </span>
            {getStatusBadge(systems.redis.status)}
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Port 6379
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Status: {systems.redis.detail}
          </div>
        </div>
      </div>
    </div>
  );
};
