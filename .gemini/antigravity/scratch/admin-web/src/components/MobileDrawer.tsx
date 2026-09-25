import React from 'react';
import { NavLink } from 'react-router-dom';
import { X, ShieldAlert, LogOut } from 'lucide-react';
import { useUIStore } from '../stores/useUIStore';

const navItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Scholarships', path: '/scholarships' },
  { label: 'Rule / Fact Versions', path: '/facts' },
  { label: 'VeriFlow', path: '/veriflow', badge: 'Rule Engine' },
  { label: 'Applications', path: '/applications' },
  { label: 'Audit Logs', path: '/audit' },
  { label: 'Settings', path: '/settings' },
];

export const MobileDrawer: React.FC = () => {
  const { isMobileDrawerOpen, setMobileDrawer } = useUIStore();

  if (!isMobileDrawerOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
        onClick={() => setMobileDrawer(false)}
      />

      {/* Drawer content */}
      <div className="relative w-4/5 max-w-xs bg-slate-950 text-white flex flex-col h-full shadow-2xl z-10 border-r border-slate-800">
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold tracking-tight">ScholarPath Admin</span>
          </div>
          <button
            onClick={() => setMobileDrawer(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setMobileDrawer(false)}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              <span>{item.label}</span>
              {item.badge && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-slate-800">
          <NavLink
            to="/login"
            onClick={() => setMobileDrawer(false)}
            className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors w-full"
          >
            <LogOut className="w-5 h-5 mr-3" />
            <span>Logout</span>
          </NavLink>
        </div>
      </div>
    </div>
  );
};
