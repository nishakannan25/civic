import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';
import { ShieldAlert, LogOut } from 'lucide-react';

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, user, isLoading, logout } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-medium text-slate-400">Verifying Admin Authorization...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Non-ADMIN role protection
  if (user && user.role !== 'ADMIN') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950 text-white">
        <div className="w-full max-w-md bg-slate-900 border border-red-500/30 p-8 rounded-2xl shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-red-500/20 text-red-500 flex items-center justify-center mx-auto">
            <ShieldAlert className="w-10 h-10" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-red-400">403 — Unauthorized Access</h2>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Your account (<span className="font-semibold text-white">{user.applicationNumber}</span>) is assigned the role <span className="text-amber-400 font-bold">{user.role}</span>. Access to ScholarPath Admin Panel is restricted exclusively to <span className="text-emerald-400 font-bold">ADMIN</span> personnel.
            </p>
          </div>
          <button
            onClick={() => logout()}
            className="w-full py-2.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold text-sm transition-colors flex items-center justify-center space-x-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Return to Sign In</span>
          </button>
        </div>
      </div>
    );
  }

  return <Outlet />;
};
