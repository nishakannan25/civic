import React from 'react';
import { History, PlusCircle, FileText, Tag, Calendar, User } from 'lucide-react';
import { FactItem } from '../types';

interface FactListTableProps {
  facts: FactItem[];
  isLoading: boolean;
  onViewHistory: (item: FactItem) => void;
  onCreateVersion: (item: FactItem) => void;
}

export const FactListTable: React.FC<FactListTableProps> = ({
  facts,
  isLoading,
  onViewHistory,
  onCreateVersion,
}) => {
  const getFactTypeBadge = (type: FactItem['factType']) => {
    switch (type) {
      case 'award_amount':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
      case 'deadline':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
      case 'eligibility':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      case 'required_documents':
        return 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20';
      case 'education_level':
        return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20';
      case 'region':
        return 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20';
      case 'application_fee':
      default:
        return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
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
              <th className="py-3 px-4">Scholarship & Fact Key</th>
              <th className="py-3 px-4">Fact Type</th>
              <th className="py-3 px-4">Version</th>
              <th className="py-3 px-4">Current Value</th>
              <th className="py-3 px-4">Effective From</th>
              <th className="py-3 px-4">Source Note & Created By</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {facts.map((fact) => (
              <tr key={fact.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                {/* Scholarship & Fact Key */}
                <td className="py-3.5 px-4">
                  <div className="font-bold text-slate-900 dark:text-slate-100 line-clamp-1">
                    {fact.scholarshipTitle}
                  </div>
                  <div className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-0.5">
                    {fact.factKey}
                  </div>
                </td>

                {/* Fact Type */}
                <td className="py-3.5 px-4">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getFactTypeBadge(
                      fact.factType
                    )}`}
                  >
                    {fact.factType}
                  </span>
                </td>

                {/* Current Version */}
                <td className="py-3.5 px-4">
                  <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 font-mono font-bold text-xs border border-blue-500/20">
                    v{fact.currentVersion}
                  </span>
                </td>

                {/* Current Value */}
                <td className="py-3.5 px-4 max-w-xs">
                  <div className="font-medium text-slate-900 dark:text-slate-100 line-clamp-2">
                    {fact.currentValue}
                  </div>
                </td>

                {/* Effective From */}
                <td className="py-3.5 px-4 font-mono text-xs text-slate-600 dark:text-slate-300">
                  {fact.effectiveFrom}
                </td>

                {/* Source Note & Created By */}
                <td className="py-3.5 px-4 max-w-xs">
                  <div className="text-xs text-slate-600 dark:text-slate-300 line-clamp-1">
                    {fact.sourceNote}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5 flex items-center">
                    <User className="w-3 h-3 mr-1" /> {fact.createdBy}
                  </div>
                </td>

                {/* Actions */}
                <td className="py-3.5 px-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => onViewHistory(fact)}
                      className="px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-1"
                      title="View complete version history"
                    >
                      <History className="w-3.5 h-3.5" />
                      <span>History</span>
                    </button>

                    <button
                      onClick={() => onCreateVersion(fact)}
                      className="px-2.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1"
                      title="Create new fact version"
                    >
                      <PlusCircle className="w-3.5 h-3.5" />
                      <span>New Version</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
