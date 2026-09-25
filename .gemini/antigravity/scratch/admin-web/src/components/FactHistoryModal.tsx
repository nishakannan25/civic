import React from 'react';
import { X, History, GitCommit, User, Calendar, FileText } from 'lucide-react';
import { FactItem } from '../types';

interface FactHistoryModalProps {
  fact: FactItem | null;
  onClose: () => void;
}

export const FactHistoryModal: React.FC<FactHistoryModalProps> = ({ fact, onClose }) => {
  if (!fact) return null;

  // Render versions in reverse order (v3, v2, v1)
  const sortedVersions = [...fact.versions].reverse();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono text-blue-500 font-bold uppercase tracking-wider">
                {fact.id} • {fact.factKey}
              </span>
            </div>
            <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 mt-0.5">
              Fact Version History Timeline
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Program: <strong className="text-slate-800 dark:text-slate-200">{fact.scholarshipTitle}</strong>
            </p>
          </div>

          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4 relative before:absolute before:left-3.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
          {sortedVersions.map((v) => {
            const isLatest = v.version === fact.currentVersion;

            return (
              <div key={v.version} className="relative pl-8 space-y-1.5">
                <div
                  className={`absolute left-1.5 top-1.5 w-4 h-4 rounded-full border-2 bg-white dark:bg-slate-900 flex items-center justify-center ${
                    isLatest
                      ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                      : 'border-slate-300 dark:border-slate-700 text-slate-400'
                  }`}
                >
                  <div className={`w-1.5 h-1.5 rounded-full ${isLatest ? 'bg-blue-600 dark:bg-blue-400' : 'bg-slate-400'}`} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                        isLatest
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                      }`}
                    >
                      v{v.version} {isLatest && '(CURRENT)'}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Effective: {v.effectiveFrom}
                    </span>
                  </div>

                  <span className="text-[11px] text-slate-400 flex items-center">
                    <User className="w-3 h-3 mr-1" /> {v.createdBy}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 text-xs md:text-sm space-y-1.5">
                  <div className="font-semibold text-slate-900 dark:text-slate-100">
                    {v.value}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 italic">
                    Note: "{v.sourceNote}"
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
          >
            Close History
          </button>
        </div>
      </div>
    </div>
  );
};
