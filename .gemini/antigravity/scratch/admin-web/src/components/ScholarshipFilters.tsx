import React, { useState, useEffect } from 'react';
import { Search, Filter, X } from 'lucide-react';
import { ScholarshipStatus, EducationLevel, ScholarshipCategory, ScholarshipFilterParams } from '../types';

interface ScholarshipFiltersProps {
  filters: ScholarshipFilterParams;
  onFilterChange: (newFilters: ScholarshipFilterParams) => void;
  onReset: () => void;
}

export const ScholarshipFilters: React.FC<ScholarshipFiltersProps> = ({
  filters,
  onFilterChange,
  onReset,
}) => {
  const [searchTerm, setSearchTerm] = useState(filters.search || '');

  // 250ms debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (filters.search || '')) {
        onFilterChange({ ...filters, search: searchTerm });
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchTerm, filters, onFilterChange]);

  return (
    <div className="p-4 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 space-y-4 shadow-xs">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Search Input */}
        <div className="lg:col-span-2 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by title, provider, category, or tag..."
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 pl-9 pr-8 text-xs md:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
          {searchTerm && (
            <button
              onClick={() => {
                setSearchTerm('');
                onFilterChange({ ...filters, search: '' });
              }}
              className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Status Select */}
        <div>
          <select
            value={filters.status || 'all'}
            onChange={(e) => onFilterChange({ ...filters, status: e.target.value as any })}
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 px-3 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        {/* Education Level Select */}
        <div>
          <select
            value={filters.educationLevel || 'all'}
            onChange={(e) => onFilterChange({ ...filters, educationLevel: e.target.value as any })}
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 px-3 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Education Levels</option>
            <option value="Secondary">Secondary</option>
            <option value="Vocational">Vocational</option>
            <option value="Undergraduate">Undergraduate</option>
            <option value="Postgraduate">Postgraduate</option>
            <option value="Doctoral">Doctoral</option>
          </select>
        </div>

        {/* Category Select */}
        <div>
          <select
            value={filters.category || 'all'}
            onChange={(e) => onFilterChange({ ...filters, category: e.target.value as any })}
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 px-3 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Categories</option>
            <option value="Merit-Based">Merit-Based</option>
            <option value="Need-Based">Need-Based</option>
            <option value="Research">Research</option>
            <option value="Minority">Minority</option>
            <option value="STEM">STEM</option>
            <option value="Arts & Humanities">Arts & Humanities</option>
          </select>
        </div>
      </div>

      {/* Active Filter Clear Tag */}
      {(filters.search || filters.status !== 'all' || filters.educationLevel !== 'all' || filters.category !== 'all') && (
        <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <span className="text-slate-500 dark:text-slate-400 flex items-center">
            <Filter className="w-3.5 h-3.5 mr-1 text-blue-500" /> Filtering active scholarships
          </span>
          <button
            onClick={() => {
              setSearchTerm('');
              onReset();
            }}
            className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
          >
            Clear All Filters
          </button>
        </div>
      )}
    </div>
  );
};
