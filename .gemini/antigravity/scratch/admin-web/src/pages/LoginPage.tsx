import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldAlert, Lock, UserCheck, ArrowRight, AlertCircle, Sparkles } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, error, clearError, isLoading } = useAuthStore();

  const [applicationNumber, setApplicationNumber] = useState('ADM-2026-001');
  const [password, setPassword] = useState('AdminSecret123!');
  const [validationError, setValidationError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!applicationNumber.trim()) {
      setValidationError('Application Number is required');
      return;
    }
    if (!password) {
      setValidationError('Password is required');
      return;
    }

    try {
      await login({
        applicationNumber: applicationNumber.trim(),
        password,
      });
      navigate(from, { replace: true });
    } catch {
      // Error handled by useAuthStore
    }
  };

  const fillMockAdmin = () => {
    setApplicationNumber('ADM-2026-001');
    setPassword('AdminSecret123!');
    setValidationError(null);
    clearError();
  };

  const fillMockNonAdmin = () => {
    setApplicationNumber('USR-9999-STUDENT');
    setPassword('UserSecret123!');
    setValidationError(null);
    clearError();
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950 text-white">
      <div className="w-full max-w-md space-y-6 bg-slate-900 p-8 rounded-2xl border border-slate-800 shadow-2xl">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center mx-auto shadow-lg shadow-blue-600/30">
            <ShieldAlert className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">ScholarPath Admin</h1>
            <p className="text-xs text-blue-400 font-semibold tracking-wide uppercase mt-1">
              Administrator Sign In
            </p>
          </div>
          <p className="text-xs text-slate-400">
            Authorized administrative personnel access portal
          </p>
        </div>

        {/* Errors display */}
        {(validationError || error) && (
          <div className="p-3.5 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start space-x-2 text-xs text-red-400">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{validationError || error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Application Number
            </label>
            <div className="relative">
              <UserCheck className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                value={applicationNumber}
                onChange={(e) => setApplicationNumber(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
                placeholder="e.g. ADM-2026-001"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-lg bg-blue-600 text-white font-semibold text-sm hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/25 flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{isLoading ? 'Authenticating...' : 'Sign In to Admin Panel'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Preset Buttons for Quick Evaluation */}
        <div className="pt-2 border-t border-slate-800 space-y-2">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block text-center">
            Development Quick Presets
          </span>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={fillMockAdmin}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-emerald-400 font-medium flex items-center justify-center space-x-1"
            >
              <Sparkles className="w-3 h-3" />
              <span>Admin Role</span>
            </button>
            <button
              type="button"
              onClick={fillMockNonAdmin}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-amber-400 font-medium flex items-center justify-center space-x-1"
            >
              <Sparkles className="w-3 h-3" />
              <span>Non-Admin Test</span>
            </button>
          </div>
        </div>

        {/* Register Link */}
        <div className="pt-3 border-t border-slate-800 text-center text-xs text-slate-400">
          New Administrator?{' '}
          <button
            type="button"
            onClick={() => navigate('/register')}
            className="text-blue-400 hover:underline font-bold"
          >
            Create Admin Account
          </button>
        </div>

        <div className="text-center text-[11px] text-slate-500">
          ScholarPath Admin Web • Application Number Authentication
        </div>
      </div>
    </div>
  );
};
