import React from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap,
  CheckCircle2,
  FileClock,
  FileText,
  GitBranch,
  CalendarCheck,
  TrendingUp
} from 'lucide-react';
import { DashboardStats } from '../types';

interface SummaryCardsProps {
  stats?: DashboardStats;
  isLoading: boolean;
}

export const DashboardSummaryCards: React.FC<SummaryCardsProps> = ({ stats, isLoading }) => {
  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-28 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Scholarships',
      value: stats.totalScholarships,
      subtitle: 'Configured programs',
      icon: GraduationCap,
      color: 'blue',
      highlight: false,
    },
    {
      title: 'Published Scholarships',
      value: stats.publishedScholarships,
      subtitle: 'Active & accepting applications',
      icon: CheckCircle2,
      color: 'emerald',
      highlight: false,
    },
    {
      title: 'Draft Scholarships',
      value: stats.draftScholarships,
      subtitle: 'Under administrative review',
      icon: FileClock,
      color: 'slate',
      highlight: false,
    },
    {
      title: 'Active Applications',
      value: stats.activeApplications.toLocaleString(),
      subtitle: 'In evaluation pipeline',
      icon: FileText,
      color: 'blue',
      highlight: false,
    },
    {
      title: 'Active VeriFlow Events',
      value: stats.activeVeriflowEvents,
      subtitle: 'Amber engine alerts active',
      icon: GitBranch,
      color: 'amber',
      highlight: true, // Amber highlight for VeriFlow
    },
    {
      title: 'Changes Published Today',
      value: stats.changesPublishedToday,
      subtitle: 'Rule & fact updates',
      icon: CalendarCheck,
      color: 'emerald',
      highlight: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        const isAmber = card.highlight;

        return (
          <div
            key={idx}
            className={`p-5 rounded-xl border transition-all duration-200 shadow-xs relative overflow-hidden ${
              isAmber
                ? 'bg-amber-500/10 dark:bg-amber-500/15 border-amber-500/40'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
            }`}
          >
            {isAmber && (
              <div className="absolute top-0 right-0 w-16 h-16 bg-amber-500/10 rounded-bl-full pointer-events-none" />
            )}

            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {card.title}
              </span>
              <div
                className={`p-2 rounded-lg ${
                  isAmber
                    ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
                    : card.color === 'emerald'
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                    : card.color === 'blue'
                    ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                    : 'bg-slate-500/10 text-slate-600 dark:text-slate-400'
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>
            </div>

            <div className="mt-3 flex items-baseline justify-between">
              <div className={`text-2xl font-bold tracking-tight ${isAmber ? 'text-amber-950 dark:text-amber-300' : ''}`}>
                {card.value}
              </div>
              {isAmber && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold border border-amber-500/30">
                  ATTENTION
                </span>
              )}
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center">
              <span>{card.subtitle}</span>
            </p>
          </div>
        );
      })}
    </div>
  );
};
