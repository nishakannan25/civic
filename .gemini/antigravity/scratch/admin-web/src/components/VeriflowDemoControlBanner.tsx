import React, { useState } from 'react';
import { Rocket, CheckCircle2, AlertCircle, Loader2, Sparkles, ArrowRight } from 'lucide-react';
import { DemoPublishResult } from '../types';

interface VeriflowDemoControlBannerProps {
  onTriggerDemo: () => Promise<DemoPublishResult>;
}

type DemoStep = 'idle' | 'publishing' | 'detecting' | 'classifying' | 'notifying' | 'completed' | 'error';

export const VeriflowDemoControlBanner: React.FC<VeriflowDemoControlBannerProps> = ({
  onTriggerDemo,
}) => {
  const [step, setStep] = useState<DemoStep>('idle');
  const [result, setResult] = useState<DemoPublishResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handlePublishClick = async () => {
    if (step !== 'idle' && step !== 'completed' && step !== 'error') return;

    setErrorMessage(null);
    setResult(null);

    try {
      // Step 1: Publishing
      setStep('publishing');
      await new Promise((res) => setTimeout(res, 600));

      // Step 2: Detecting
      setStep('detecting');
      await new Promise((res) => setTimeout(res, 700));

      // Step 3: Classifying
      setStep('classifying');
      await new Promise((res) => setTimeout(res, 700));

      // Step 4: Notifying
      setStep('notifying');

      const res = await onTriggerDemo();

      await new Promise((resolve) => setTimeout(resolve, 500));
      setResult(res);
      setStep('completed');
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to publish demo rule change via backend.');
      setStep('error');
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-900 via-slate-900 to-indigo-950 text-white border border-blue-500/30 shadow-xl space-y-4 relative overflow-hidden">
      <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left Description */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              REALTIME DEMO SUITE
            </span>
            <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
          </div>
          <h3 className="text-base font-bold text-slate-100 flex items-center">
            VeriFlow Policy Impact Demonstration
          </h3>
          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            Publish a controlled scholarship rule change to demonstrate VeriFlow in action.
            Appends mandatory document <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-300">Bank Statement</code> to <strong>ScholarPath Merit Scholarship 2026</strong> and evaluates active applicant application <code className="text-blue-300 font-mono">APP-2026-9012</code> in real-time.
          </p>
        </div>

        {/* Action Button */}
        <div className="shrink-0 flex items-center">
          <button
            onClick={handlePublishClick}
            disabled={step === 'publishing' || step === 'detecting' || step === 'classifying' || step === 'notifying'}
            className={`px-5 py-3 rounded-xl font-bold text-xs shadow-lg transition-all flex items-center space-x-2 border ${
              step === 'publishing' || step === 'detecting' || step === 'classifying' || step === 'notifying'
                ? 'bg-slate-800 border-slate-700 text-slate-400 cursor-not-allowed'
                : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 border-emerald-400 shadow-emerald-500/20 active:scale-95'
            }`}
          >
            {step === 'idle' || step === 'completed' || step === 'error' ? (
              <>
                <Rocket className="w-4 h-4 text-slate-950" />
                <span>PUBLISH DEMO RULE CHANGE</span>
              </>
            ) : (
              <>
                <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                <span className="capitalize">{step}...</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Progress Execution Pipeline Indicator */}
      {(step !== 'idle' || result || errorMessage) && (
        <div className="pt-3 border-t border-slate-800/80">
          {step !== 'idle' && step !== 'completed' && step !== 'error' && (
            <div className="flex items-center space-x-4 text-xs font-mono text-slate-300">
              <span className={step === 'publishing' ? 'text-amber-400 font-bold animate-pulse' : 'text-slate-500'}>
                1. Publishing...
              </span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span className={step === 'detecting' ? 'text-amber-400 font-bold animate-pulse' : 'text-slate-500'}>
                2. Detecting...
              </span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span className={step === 'classifying' ? 'text-amber-400 font-bold animate-pulse' : 'text-slate-500'}>
                3. Classifying...
              </span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span className={step === 'notifying' ? 'text-amber-400 font-bold animate-pulse' : 'text-slate-500'}>
                4. Notifying...
              </span>
            </div>
          )}

          {step === 'completed' && result && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex flex-wrap items-center justify-between text-xs gap-3">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>✓ Rule change published to SQLite/Redis/WebSocket</span>
              </div>

              <div className="flex items-center space-x-4 text-slate-300 font-mono text-[11px]">
                <span>
                  Version: <strong className="text-white font-bold">{result.oldVersion} → {result.newVersion}</strong>
                </span>
                <span>
                  Classification: <strong className="text-red-400 font-bold uppercase">{result.classification}</strong>
                </span>
                <span>
                  Applicants Notified: <strong className="text-amber-400 font-bold">{result.affectedApplicationsCount}</strong>
                </span>
              </div>
            </div>
          )}

          {step === 'error' && errorMessage && (
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center space-x-2 text-xs text-red-400 font-medium">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>Execution failed: {errorMessage}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
