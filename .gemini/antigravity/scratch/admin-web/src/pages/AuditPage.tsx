import React, { useState } from 'react';
import { ScrollText } from 'lucide-react';
import { useAuditLogs, useVerifyAuditIntegrity } from '../hooks/useAudit';
import { AuditLogEntry } from '../types';
import { AuditIntegrityChecker } from '../components/AuditIntegrityChecker';
import { AuditLogTable } from '../components/AuditLogTable';
import { AuditDetailsModal } from '../components/AuditDetailsModal';

export const AuditPage: React.FC = () => {
  const { data: logs = [], isLoading } = useAuditLogs();
  const verifyIntegrityMutation = useVerifyAuditIntegrity();
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);

  const handleVerifyIntegrity = async () => {
    return await verifyIntegrityMutation.mutateAsync();
  };

  return (
    <div className="space-y-6 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center">
            <ScrollText className="w-5 h-5 mr-2 text-emerald-500" />
            Append-Only Cryptographic Audit Log
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Tamper-evident system activity ledger backed by cryptographic SHA-256 hash chains
          </p>
        </div>
      </div>

      {/* Audit Integrity Checker Banner */}
      <AuditIntegrityChecker onVerify={handleVerifyIntegrity} />

      {/* Audit Log Table */}
      <AuditLogTable
        logs={logs}
        isLoading={isLoading}
        onSelectLog={(log) => setSelectedLog(log)}
      />

      {/* Audit Details Modal */}
      <AuditDetailsModal log={selectedLog} onClose={() => setSelectedLog(null)} />
    </div>
  );
};
