import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, GraduationCap } from 'lucide-react';
import {
  useScholarshipsList,
  usePublishScholarship,
  useArchiveScholarship,
} from '../hooks/useScholarships';
import { ScholarshipItem, ScholarshipFilterParams } from '../types';
import { ScholarshipFilters } from '../components/ScholarshipFilters';
import { ScholarshipListTable } from '../components/ScholarshipListTable';
import { ConfirmModal } from '../components/ConfirmModal';
import { ScholarshipDetailModal } from '../components/ScholarshipDetailModal';

export const ScholarshipsPage: React.FC = () => {
  const navigate = useNavigate();

  const [filters, setFilters] = useState<ScholarshipFilterParams>({
    search: '',
    status: 'all',
    educationLevel: 'all',
    category: 'all',
    region: 'all',
  });

  const { data: scholarships = [], isLoading } = useScholarshipsList(filters);
  const publishMutation = usePublishScholarship();
  const archiveMutation = useArchiveScholarship();

  // Modals state
  const [selectedItem, setSelectedItem] = useState<ScholarshipItem | null>(null);
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'publish' | 'archive';
    item: ScholarshipItem | null;
  }>({
    isOpen: false,
    type: 'publish',
    item: null,
  });

  const handlePublishClick = (item: ScholarshipItem) => {
    setConfirmModal({ isOpen: true, type: 'publish', item });
  };

  const handleArchiveClick = (item: ScholarshipItem) => {
    setConfirmModal({ isOpen: true, type: 'archive', item });
  };

  const handleConfirmAction = async () => {
    if (!confirmModal.item) return;

    try {
      if (confirmModal.type === 'publish') {
        await publishMutation.mutateAsync(confirmModal.item.id);
      } else {
        await archiveMutation.mutateAsync(confirmModal.item.id);
      }
    } finally {
      setConfirmModal({ isOpen: false, type: 'publish', item: null });
    }
  };

  return (
    <div className="space-y-6 pb-10">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center">
            <GraduationCap className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
            Scholarship Management
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Create, edit, publish, and archive national & state financial assistance programs
          </p>
        </div>

        <button
          onClick={() => navigate('/scholarships/new')}
          className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md flex items-center justify-center space-x-2 transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Create Scholarship</span>
        </button>
      </div>

      {/* Filter Controls */}
      <ScholarshipFilters
        filters={filters}
        onFilterChange={(newFilters) => setFilters(newFilters)}
        onReset={() =>
          setFilters({
            search: '',
            status: 'all',
            educationLevel: 'all',
            category: 'all',
            region: 'all',
          })
        }
      />

      {/* Scholarship Table */}
      <ScholarshipListTable
        scholarships={scholarships}
        isLoading={isLoading}
        onView={(item) => setSelectedItem(item)}
        onEdit={(item) => navigate(`/scholarships/edit/${item.id}`)}
        onPublishClick={handlePublishClick}
        onArchiveClick={handleArchiveClick}
      />

      {/* Detail Modal */}
      <ScholarshipDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={confirmModal.isOpen}
        type={confirmModal.type}
        itemTitle={confirmModal.item?.title || ''}
        isSubmitting={publishMutation.isPending || archiveMutation.isPending}
        onConfirm={handleConfirmAction}
        onCancel={() => setConfirmModal({ isOpen: false, type: 'publish', item: null })}
      />
    </div>
  );
};
