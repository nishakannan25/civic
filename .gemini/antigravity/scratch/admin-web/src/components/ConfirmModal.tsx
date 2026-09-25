import React from 'react';
import { AlertTriangle, Send, Archive, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  type: 'publish' | 'archive';
  itemTitle: string;
  isSubmitting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  type,
  itemTitle,
  isSubmitting,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  const isPublish = type === 'publish';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center space-x-2">
            <div
              className={`p-2 rounded-lg ${
                isPublish
                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                  : 'bg-red-500/10 text-red-600 dark:text-red-400'
              }`}
            >
              {isPublish ? <Send className="w-5 h-5" /> : <Archive className="w-5 h-5" />}
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
              {isPublish ? 'Publish Scholarship Program' : 'Archive Scholarship Program'}
            </h3>
          </div>
          <button onClick={onCancel} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs md:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          {isPublish ? (
            <>
              Are you sure you want to publish <strong className="text-slate-900 dark:text-white">"{itemTitle}"</strong>? This will make the program active and visible for applicant evaluations.
            </>
          ) : (
            <>
              Are you sure you want to archive <strong className="text-slate-900 dark:text-white">"{itemTitle}"</strong>? This will remove it from active evaluations while maintaining immutable audit history.
            </>
          )}
        </p>

        <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isSubmitting}
            className={`px-4 py-2 rounded-lg text-xs font-semibold text-white transition-colors shadow-xs ${
              isPublish ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-red-600 hover:bg-red-500'
            }`}
          >
            {isSubmitting
              ? isPublish
                ? 'Publishing...'
                : 'Archiving...'
              : isPublish
              ? 'Confirm Publish'
              : 'Confirm Archive'}
          </button>
        </div>
      </div>
    </div>
  );
};
