import React from 'react';
import { Link } from 'react-router-dom';
import {
  PlusCircle,
  GraduationCap,
  FileCheck2,
  GitBranch,
  ShieldCheck,
  ArrowRight
} from 'lucide-react';

export const DashboardQuickActions: React.FC = () => {
  const actions = [
    {
      label: 'Create Scholarship',
      description: 'Define program rules & funding tier',
      path: '/scholarships',
      icon: PlusCircle,
      color: 'blue',
    },
    {
      label: 'Manage Scholarships',
      description: 'Review active & draft policies',
      path: '/scholarships',
      icon: GraduationCap,
      color: 'blue',
    },
    {
      label: 'Manage Facts',
      description: 'Fact versions & state schema',
      path: '/facts',
      icon: FileCheck2,
      color: 'blue',
    },
    {
      label: 'Open VeriFlow',
      description: 'Rule engine evaluator & tree',
      path: '/veriflow',
      icon: GitBranch,
      color: 'amber',
      highlight: true,
    },
    {
      label: 'View Audit Logs',
      description: 'Cryptographic system audit stream',
      path: '/audit',
      icon: ShieldCheck,
      color: 'slate',
    },
  ];

  return (
    <div className="p-5 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
      <h3 className="font-bold text-base tracking-tight">Quick Actions</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          const isAmber = act.highlight;

          return (
            <Link
              key={idx}
              to={act.path}
              className={`p-3.5 rounded-lg border transition-all duration-200 group flex flex-col justify-between hover:shadow-md ${
                isAmber
                  ? 'bg-amber-500/10 border-amber-500/30 hover:border-amber-500/60'
                  : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 hover:border-blue-500/40'
              }`}
            >
              <div>
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2.5 ${
                    isAmber
                      ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
                      : 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div className="font-bold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {act.label}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-normal">
                  {act.description}
                </p>
              </div>

              <div className="mt-3 flex items-center text-xs font-semibold text-blue-600 dark:text-blue-400 group-hover:translate-x-1 transition-transform">
                <span>Launch</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
