import React, { useState } from 'react';
import { Search, FileCheck2, Info, Plus } from 'lucide-react';
import { useFactsList, useCreateFactVersion } from '../hooks/useFacts';
import { FactItem, CreateFactVersionPayload } from '../types';
import { FactListTable } from '../components/FactListTable';
import { FactHistoryModal } from '../components/FactHistoryModal';
import { CreateFactVersionModal } from '../components/CreateFactVersionModal';

export const FactsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const { data: facts = [], isLoading } = useFactsList(search);
  const createVersionMutation = useCreateFactVersion();

  const [historyFact, setHistoryFact] = useState<FactItem | null>(null);
  const [createFact, setCreateFact] = useState<FactItem | null>(null);

  const handleCreateVersionSubmit = async (payload: CreateFactVersionPayload) => {
    if (!createFact) return;
    try {
      await createVersionMutation.mutateAsync({
        id: createFact.id,
        payload,
      });
      setCreateFact(null);
    } catch {
      // Error handled inside modal
    }
  };

  return (
    <div className="space-y-6 pb-10">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center">
            <FileCheck2 className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
            Fact Version Management
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Immutable versioned scholarship rule parameters (award amounts, eligibility ceilings, required document schemas)
          </p>
        </div>
      </div>

      {/* Governance Banner */}
      <div className="p-4 rounded-xl bg-slate-900 text-white border border-slate-800 flex items-start space-x-3 shadow-md">
        <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed space-y-1">
          <div className="font-bold text-slate-100">
            Immutable Audit Preservation Policy:
          </div>
          <p className="text-slate-300">
            Creating a new fact version <span className="text-emerald-400 font-semibold">NEVER overwrites</span> previous versions. All past versions (v1, v2, v3...) remain permanently archived for cryptographic evaluation and audit verification. Publishing automatically triggers the <strong>VeriFlow rule engine</strong>.
          </p>
        </div>
      </div>

      {/* Search Input */}
      <div className="p-4 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search facts by scholarship, key, type, or value..."
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg py-2 pl-9 pr-4 text-xs md:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Fact List Table */}
      <FactListTable
        facts={facts}
        isLoading={isLoading}
        onViewHistory={(item) => setHistoryFact(item)}
        onCreateVersion={(item) => setCreateFact(item)}
      />

      {/* Version History Modal */}
      <FactHistoryModal fact={historyFact} onClose={() => setHistoryFact(null)} />

      {/* Create New Version Modal */}
      <CreateFactVersionModal
        fact={createFact}
        isOpen={Boolean(createFact)}
        isSubmitting={createVersionMutation.isPending}
        onSubmit={handleCreateVersionSubmit}
        onCancel={() => setCreateFact(null)}
      />
    </div>
  );
};
