import React from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Sun, Moon, Bell, ShieldCheck } from 'lucide-react';
import { useUIStore } from '../stores/useUIStore';

const titleMap: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Admin Dashboard', subtitle: 'System overview & real-time monitoring' },
  '/scholarships': { title: 'Scholarship Management', subtitle: 'Configure programs and funding rules' },
  '/facts': { title: 'Rule & Fact Versions', subtitle: 'Fact store state and active engine policies' },
  '/veriflow': { title: 'VeriFlow Rule Engine', subtitle: 'Visual logic evaluation & execution flow' },
  '/applications': { title: 'Applications', subtitle: 'Review and verify applicant submissions' },
  '/audit': { title: 'Audit Logs', subtitle: 'Immutable system audit trail & history' },
  '/settings': { title: 'System Settings', subtitle: 'Admin controls and global parameters' },
  '/login': { title: 'Admin Login', subtitle: 'Authenticate into ScholarPath Admin' },
};

export const TopNav: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme, toggleMobileDrawer } = useUIStore();

  const currentInfo = titleMap[location.pathname] || {
    title: 'ScholarPath Admin',
    subtitle: 'Government & Scholarship Operations Console'
  };

  return (
    <header
      className="h-16 border-b px-4 md:px-6 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md transition-colors duration-200"
      style={{
        backgroundColor: theme === 'dark' ? 'rgba(17, 24, 39, 0.85)' : 'rgba(255, 255, 255, 0.85)',
        borderColor: 'var(--border-color)'
      }}
    >
      <div className="flex items-center space-x-3">
        <button
          onClick={toggleMobileDrawer}
          className="md:hidden p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-base md:text-lg font-bold tracking-tight">{currentInfo.title}</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
            {currentInfo.subtitle}
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Admin Portal Active</span>
        </div>

        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg border hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors"
          style={{ borderColor: 'var(--border-color)' }}
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? <Moon className="w-4 h-4 text-slate-700" /> : <Sun className="w-4 h-4 text-amber-400" />}
        </button>

        <div className="flex items-center space-x-2 border-l pl-3" style={{ borderColor: 'var(--border-color)' }}>
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
            AD
          </div>
          <div className="hidden lg:flex flex-col text-left text-xs">
            <span className="font-semibold leading-tight">Admin Officer</span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">admin@scholarpath.gov</span>
          </div>
        </div>
      </div>
    </header>
  );
};
