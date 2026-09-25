import React from 'react';
import { Settings, Sliders, Database, Server, Key } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight">System Settings</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Global configuration, API endpoints, and admin security settings
          </p>
        </div>
      </div>

      <div className="p-8 text-center rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800">
        <div className="w-16 h-16 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto mb-4">
          <Settings className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold">Admin Configuration & Parameters</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mt-2">
          [Phase 1 Placeholder] System parameter toggles, API key management, and environment variables will be activated in Phase 2.
        </p>
      </div>
    </div>
  );
};
