import React from 'react';
import { X, GraduationCap, DollarSign, Calendar, Tag, ShieldCheck } from 'lucide-react';
import { ScholarshipItem } from '../types';

interface ScholarshipDetailModalProps {
  item: ScholarshipItem | null;
  onClose: () => void;
}

export const ScholarshipDetailModal: React.FC<ScholarshipDetailModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-blue-500 font-bold uppercase tracking-wider">
              {item.id} • {item.status.toUpperCase()}
            </span>
            <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 mt-0.5">
              {item.title}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{item.provider}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs md:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          {item.description}
        </p>

        <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 text-xs">
          <div>
            <span className="text-slate-400 font-semibold block uppercase tracking-wider text-[10px]">
              Financial Grant Amount
            </span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
              ₹{item.amount.toLocaleString('en-IN')}
            </span>
          </div>

          <div>
            <span className="text-slate-400 font-semibold block uppercase tracking-wider text-[10px]">
              Application Deadline
            </span>
            <span className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100">
              {item.deadline}
            </span>
          </div>
        </div>

        {/* Education Levels & Categories */}
        <div className="space-y-3">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Education Levels
            </span>
            <div className="flex flex-wrap gap-1.5">
              {item.educationLevels.map((lvl, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs font-medium">
                  {lvl}
                </span>
              ))}
            </div>
          </div>

          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Categories
            </span>
            <div className="flex flex-wrap gap-1.5">
              {item.categories.map((cat, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-medium">
                  {cat}
                </span>
              ))}
            </div>
          </div>

          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Required Documents
            </span>
            <div className="flex flex-wrap gap-1.5">
              {item.requiredDocuments.map((doc, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs">
                  {doc}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
};
