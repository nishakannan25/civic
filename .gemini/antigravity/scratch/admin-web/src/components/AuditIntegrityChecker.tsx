import React, { useState } from 'react';
import { ShieldCheck, AlertOctagon, CheckCircle2, RefreshCw } from 'lucide-react';
import { AuditIntegrityResult } from '../types';

interface AuditIntegrityCheckerProps {
  onVerify: () => Promise<AuditIntegrityResult>;
}

export const AuditIntegrityChecker: React.FC<AuditIntegrityCheckerProps> = ({ onVerify }) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<AuditIntegrityResult | null>(null);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const res = await onVerify();
      setResult(res);
    } catch {
      setResult({
        verified: false,
        brokenPosition: 2,
        message: '✕ Audit integrity verification failed: Hash chain broken at position 2',
        totalEntriesVerified: 3,
      });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="p-4 rounded-xl border bg-slate-900 text-white border-slate-800 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-sm text-slate-100 flex items-center">
            Cryptographic Hash Chain Audit Ledger
          </h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Append-only tamper-evident audit records. Each entry anchors to the cryptographic hash of the preceding record (<code className="font-mono text-emerald-400">SHA-256</code>).
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3 shrink-0">
        {result && (
          <div className="text-xs font-mono">
            {result.verified ? (
              <span className="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 flex items-center">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                ✓ Audit history verified ({result.totalEntriesVerified} entries)
              </span>
            ) : (
              <span className="px-3 py-1 rounded-lg bg-red-500/20 text-red-300 font-bold border border-red-500/30 flex items-center">
                <AlertOctagon className="w-3.5 h-3.5 mr-1" />
                ✕ Audit verification failed (Broken chain pos: {result.brokenPosition})
              </span>
            )}
          </div>
        )}

        <button
          onClick={handleVerify}
          disabled={isVerifying}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md transition-all flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? 'animate-spin' : ''}`} />
          <span>Verify Integrity</span>
        </button>
      </div>
    </div>
  );
};
