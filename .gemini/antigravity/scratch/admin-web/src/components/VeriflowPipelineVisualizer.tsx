import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, ArrowRight, Zap, Bell, Shield } from 'lucide-react';
import { VeriflowPipelineStep } from '../types';

interface VeriflowPipelineVisualizerProps {
  activeStep?: VeriflowPipelineStep;
}

const steps: { key: VeriflowPipelineStep; label: string; icon: React.FC<{ className?: string }> }[] = [
  { key: 'FACT_PUBLISHED', label: 'FACT PUBLISHED', icon: Zap },
  { key: 'CHANGE_DETECTED', label: 'CHANGE DETECTED', icon: AlertTriangle },
  { key: 'APPLICATIONS_IDENTIFIED', label: 'APPLICATIONS IDENTIFIED', icon: Shield },
  { key: 'CLASSIFIED', label: 'CLASSIFIED', icon: CheckCircle2 },
  { key: 'APPLICANT_NOTIFIED', label: 'APPLICANT NOTIFIED', icon: Bell },
  { key: 'RECOVERY_DECISION', label: 'RECOVERY DECISION', icon: CheckCircle2 },
];

export const VeriflowPipelineVisualizer: React.FC<VeriflowPipelineVisualizerProps> = ({
  activeStep = 'RECOVERY_DECISION',
}) => {
  const activeIndex = steps.findIndex((s) => s.key === activeStep);

  return (
    <div className="p-5 rounded-2xl border bg-slate-900 text-white border-slate-800 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
          </span>
          <h3 className="font-bold text-sm tracking-wide text-amber-400 uppercase">
            VeriFlow Realtime Policy Pipeline Engine
          </h3>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
          WEBSOCKET ACTIVE
        </span>
      </div>

      <div className="overflow-x-auto py-2">
        <div className="flex items-center min-w-[700px] justify-between">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isCompleted = idx <= activeIndex;
            const isCurrent = idx === activeIndex;

            return (
              <React.Fragment key={step.key}>
                {/* Step Item */}
                <div className="flex flex-col items-center space-y-2 relative group">
                  <motion.div
                    initial={{ scale: 0.9 }}
                    animate={{ scale: isCurrent ? 1.1 : 1 }}
                    transition={{ duration: 0.3 }}
                    className={`w-10 h-10 rounded-xl flex items-center justify-center border transition-colors ${
                      isCurrent
                        ? 'bg-amber-500 border-amber-400 text-slate-950 shadow-lg shadow-amber-500/20'
                        : isCompleted
                        ? 'bg-blue-600/20 border-blue-500/40 text-blue-400'
                        : 'bg-slate-800 border-slate-700 text-slate-500'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </motion.div>

                  <span
                    className={`text-[10px] font-bold tracking-wider text-center max-w-[90px] ${
                      isCurrent
                        ? 'text-amber-400'
                        : isCompleted
                        ? 'text-slate-200'
                        : 'text-slate-500'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>

                {/* Arrow Connector */}
                {idx < steps.length - 1 && (
                  <div className="flex-1 flex justify-center items-center px-1">
                    <motion.div
                      animate={{ opacity: idx < activeIndex ? 1 : 0.4 }}
                      className="w-full flex items-center justify-center"
                    >
                      <ArrowRight
                        className={`w-4 h-4 ${
                          idx < activeIndex ? 'text-blue-400' : 'text-slate-700'
                        }`}
                      />
                    </motion.div>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};
