import React, { useState } from 'react';
import { X, ArrowRight, ShieldCheck, AlertCircle, FileDiff } from 'lucide-react';
import { FactItem, CreateFactVersionPayload } from '../types';

interface CreateFactVersionModalProps {
  fact: FactItem | null;
  isOpen: boolean;
  isSubmitting: boolean;
  onSubmit: (payload: CreateFactVersionPayload) => Promise<void>;
  onCancel: () => void;
}

export const CreateFactVersionModal: React.FC<CreateFactVersionModalProps> = ({
  fact,
  isOpen,
  isSubmitting,
  onSubmit,
  onCancel,
}) => {
  if (!isOpen || !fact) return null;

  const [newValue, setNewValue] = useState(fact.currentValue);
  const [effectiveFrom, setEffectiveFrom] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [sourceNote, setSourceNote] = useState('');
  const [showDiff, setShowDiff] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const newVersionNumber = fact.currentVersion + 1;

  const handlePreviewDiff = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!newValue.trim()) {
      setError('New fact value is required.');
      return;
    }
    if (!effectiveFrom) {
      setError('Effective date is required.');
      return;
    }
    if (!sourceNote.trim()) {
      setError('Source note / policy gazette reference is required.');
      return;
    }

    setShowDiff(true);
  };

  const handleFinalPublish = async () => {
    try {
      await onSubmit({
        newValue: newValue.trim(),
        effectiveFrom,
        sourceNote: sourceNote.trim(),
      });
      setShowDiff(false);
    } catch (err: any) {
      setError(err.message || 'Failed to publish fact version.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-blue-500 font-bold uppercase tracking-wider">
              {fact.factKey} • Creating Version v{newVersionNumber}
            </span>
            <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 mt-0.5">
              Create New Fact Version
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Program: <strong className="text-slate-800 dark:text-slate-200">{fact.scholarshipTitle}</strong>
            </p>
          </div>

          <button onClick={onCancel} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {!showDiff ? (
          /* Step 1: Input Form */
          <form onSubmit={handlePreviewDiff} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Current Version (v{fact.currentVersion}) Value
              </label>
              <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800/60 text-xs text-slate-600 dark:text-slate-300 font-mono">
                {fact.currentValue}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                New Version (v{newVersionNumber}) Value *
              </label>
              <textarea
                rows={3}
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="Enter updated fact value..."
                className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Effective From Date *
                </label>
                <input
                  type="date"
                  value={effectiveFrom}
                  onChange={(e) => setEffectiveFrom(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Source Note / Gazette Reference *
                </label>
                <input
                  type="text"
                  value={sourceNote}
                  onChange={(e) => setSourceNote(e.target.value)}
                  placeholder="e.g. Policy Gazette #2026/102C"
                  className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-3 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>

              <button
                type="submit"
                className="px-5 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-colors shadow-xs flex items-center space-x-1.5"
              >
                <FileDiff className="w-4 h-4" />
                <span>Preview Diff & Confirm</span>
              </button>
            </div>
          </form>
        ) : (
          /* Step 2: Side-by-Side Diff Preview & Publication Confirmation */
          <div className="space-y-5">
            <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-600 dark:text-blue-300">
              <strong>Publication Workflow Trigger:</strong> Confirming publication will create <strong>v{newVersionNumber}</strong>, preserve <strong>v{fact.currentVersion}</strong> intact, log an audit trail entry, publish a Redis event, and initiate VeriFlow rule re-evaluation.
            </div>

            {/* Side-by-Side Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Old Version */}
              <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 space-y-2">
                <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider block">
                  OLD VERSION {fact.currentVersion}
                </span>
                <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 font-mono">
                  {fact.currentValue}
                </div>
                <div className="text-[11px] text-slate-500">
                  Source: "{fact.sourceNote}"
                </div>
              </div>

              {/* New Version */}
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
                <span className="text-[10px] font-mono font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                  NEW VERSION {newVersionNumber}
                </span>
                <div className="text-xs font-semibold text-emerald-950 dark:text-emerald-200 font-mono">
                  {newValue}
                </div>
                <div className="text-[11px] text-emerald-700 dark:text-emerald-400">
                  Source: "{sourceNote}"
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center pt-3 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                onClick={() => setShowDiff(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Back to Edit
              </button>

              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={onCancel}
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={handleFinalPublish}
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors shadow-xs flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>{isSubmitting ? 'Publishing Pipeline...' : 'Publish Fact Version'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
