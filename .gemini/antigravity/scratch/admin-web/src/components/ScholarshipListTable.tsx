import React from 'react';
import { Eye, Edit2, Send, Archive, Calendar, DollarSign, Tag, GraduationCap } from 'lucide-react';
import { ScholarshipItem } from '../types';

interface ScholarshipListTableProps {
  scholarships: ScholarshipItem[];
  isLoading: boolean;
  onView: (item: ScholarshipItem) => void;
  onEdit: (item: ScholarshipItem) => void;
  onPublishClick: (item: ScholarshipItem) => void;
  onArchiveClick: (item: ScholarshipItem) => void;
}

export const ScholarshipListTable: React.FC<ScholarshipListTableProps> = ({
  scholarships,
  isLoading,
  onView,
  onEdit,
  onPublishClick,
  onArchiveClick,
}) => {
  const getStatusBadge = (status: ScholarshipItem['status']) => {
    switch (status) {
      case 'published':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            Published
          </span>
        );
      case 'draft':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
            Draft
          </span>
        );
      case 'archived':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/10 text-slate-500 dark:text-slate-400 border border-slate-500/20">
            Archived
          </span>
        );
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

  if (scholarships.length === 0) {
    return (
      <div className="rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-12 text-center">
        <GraduationCap className="w-10 h-10 text-slate-400 mx-auto mb-3" />
        <h3 className="font-bold text-base">No Scholarships Found</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
          No scholarship records matched your query. Try broadening your filter parameters or create a new scholarship program.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs md:text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[11px] font-bold">
            <tr>
              <th className="py-3 px-4">Title & Provider</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Deadline</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Categories & Roles</th>
              <th className="py-3 px-4">Updated</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {scholarships.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                {/* Title & Provider */}
                <td className="py-3.5 px-4">
                  <div className="font-bold text-slate-900 dark:text-slate-100 line-clamp-1">
                    {item.title}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {item.provider} • <span className="font-mono text-[10px]">{item.id}</span>
                  </div>
                </td>

                {/* Amount */}
                <td className="py-3.5 px-4 font-semibold text-emerald-600 dark:text-emerald-400">
                  ₹{item.amount.toLocaleString('en-IN')}
                </td>

                {/* Deadline */}
                <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300 font-mono text-xs">
                  {item.deadline}
                </td>

                {/* Status */}
                <td className="py-3.5 px-4">{getStatusBadge(item.status)}</td>

                {/* Categories & Roles */}
                <td className="py-3.5 px-4">
                  <div className="flex flex-wrap gap-1">
                    {item.categories.map((cat, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[10px] font-medium"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                </td>

                {/* Updated At */}
                <td className="py-3.5 px-4 text-slate-400 text-xs">
                  {new Date(item.updatedAt).toLocaleDateString()}
                </td>

                {/* Actions */}
                <td className="py-3.5 px-4 text-right">
                  <div className="flex items-center justify-end space-x-1">
                    <button
                      onClick={() => onView(item)}
                      className="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => onEdit(item)}
                      className="p-1.5 rounded hover:bg-blue-500/10 text-blue-600 dark:text-blue-400 transition-colors"
                      title="Edit scholarship"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>

                    {item.status === 'draft' && (
                      <button
                        onClick={() => onPublishClick(item)}
                        className="p-1.5 rounded hover:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 transition-colors"
                        title="Publish scholarship"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    )}

                    {item.status !== 'archived' && (
                      <button
                        onClick={() => onArchiveClick(item)}
                        className="p-1.5 rounded hover:bg-red-500/10 text-red-600 dark:text-red-400 transition-colors"
                        title="Archive scholarship"
                      >
                        <Archive className="w-4 h-4" />
                      </button>
                    )}
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
