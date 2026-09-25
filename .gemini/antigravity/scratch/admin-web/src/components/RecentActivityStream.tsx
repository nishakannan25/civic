import React from 'react';
import {
  GitBranch,
  GraduationCap,
  FileCheck2,
  BellRing,
  ShieldCheck,
  Clock
} from 'lucide-react';
import { ActivityItem } from '../types';

interface ActivityStreamProps {
  activities?: ActivityItem[];
  isLoading: boolean;
}

export const RecentActivityStream: React.FC<ActivityStreamProps> = ({ activities, isLoading }) => {
  const getIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'VERIFLOW_EVENT':
        return <GitBranch className="w-4 h-4 text-amber-500" />;
      case 'SCHOLARSHIP_PUBLISHED':
        return <GraduationCap className="w-4 h-4 text-emerald-500" />;
      case 'FACT_VERSION_CREATED':
        return <FileCheck2 className="w-4 h-4 text-blue-500" />;
      case 'RECOVERY_DECISION':
        return <ShieldCheck className="w-4 h-4 text-amber-600" />;
      case 'APPLICANT_NOTIFIED':
      default:
        return <BellRing className="w-4 h-4 text-slate-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="p-5 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 space-y-4">
        <div className="h-4 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-14 bg-slate-100 dark:bg-slate-800/40 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-5 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs">
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-base tracking-tight flex items-center">
            <Clock className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
            Recent System Activity
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Audit logs, rule engine events, and scholarship publishing history
          </p>
        </div>
      </div>

      <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
        {activities?.map((item) => (
          <div key={item.id} className="py-3.5 flex items-start space-x-3 group">
            <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 shrink-0 mt-0.5">
              {getIcon(item.type)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">
                  {item.title}
                </span>
                <span className="text-[11px] text-slate-400 shrink-0 ml-2">{item.timestamp}</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                {item.description}
              </p>
            </div>

            {item.badge && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300 font-semibold border border-amber-500/30 shrink-0">
                {item.badge}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
