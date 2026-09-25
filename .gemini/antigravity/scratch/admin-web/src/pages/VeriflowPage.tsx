import React, { useState } from 'react';
import { Cpu, RefreshCw, Filter } from 'lucide-react';
import { useVeriflowEvents, useTriggerDemoPublish } from '../hooks/useVeriflow';
import { VeriflowEvent, VeriflowClassification } from '../types';
import { VeriflowPipelineVisualizer } from '../components/VeriflowPipelineVisualizer';
import { VeriflowEventsTable } from '../components/VeriflowEventsTable';
import { VeriflowEventDetailsModal } from '../components/VeriflowEventDetailsModal';
import { VeriflowDemoControlBanner } from '../components/VeriflowDemoControlBanner';

export const VeriflowPage: React.FC = () => {
  const { data: events = [], isLoading, refetch, isFetching } = useVeriflowEvents();
  const triggerDemoMutation = useTriggerDemoPublish();
  const [selectedEvent, setSelectedEvent] = useState<VeriflowEvent | null>(null);
  const [filterClassification, setFilterClassification] = useState<
    VeriflowClassification | 'all'
  >('all');

  const filteredEvents =
    filterClassification === 'all'
      ? events
      : events.filter((e) => e.classification === filterClassification);

  const handleTriggerDemo = async () => {
    return await triggerDemoMutation.mutateAsync();
  };

  return (
    <div className="space-y-6 pb-10">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center">
            <Cpu className="w-5 h-5 mr-2 text-amber-500" />
            VeriFlow Control Center
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Realtime monitoring of live policy changes, AI impact classification, applicant notifications & recovery decisions
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="px-3.5 py-2 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-1.5 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          <span>Sync Events</span>
        </button>
      </div>

      {/* Live VeriFlow Demo Control Banner */}
      <VeriflowDemoControlBanner onTriggerDemo={handleTriggerDemo} />

      {/* Live Framer Motion Pipeline Visualizer */}
      <VeriflowPipelineVisualizer activeStep="RECOVERY_DECISION" />

      {/* Classification Filter Bar */}
      <div className="flex items-center justify-between p-4 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Filter Impact:
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {(['all', 'blocking', 'informational', 'cosmetic'] as const).map((cls) => {
            const active = filterClassification === cls;
            return (
              <button
                key={cls}
                onClick={() => setFilterClassification(cls)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors border capitalize ${
                  active
                    ? 'bg-amber-500 border-amber-500 text-slate-950 font-bold'
                    : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                }`}
              >
                {cls}
              </button>
            );
          })}
        </div>
      </div>

      {/* Change Events Table */}
      <VeriflowEventsTable
        events={filteredEvents}
        isLoading={isLoading}
        onSelectEvent={(event) => setSelectedEvent(event)}
      />

      {/* Event Details Drawer Modal */}
      <VeriflowEventDetailsModal
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
};
