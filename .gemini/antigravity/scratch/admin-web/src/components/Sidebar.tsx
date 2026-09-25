import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GraduationCap,
  FileCheck2,
  GitBranch,
  FileText,
  ShieldCheck,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import { useUIStore } from '../stores/useUIStore';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, category: 'normal' },
  { label: 'Scholarships', path: '/scholarships', icon: GraduationCap, category: 'normal' },
  { label: 'Rule / Fact Versions', path: '/facts', icon: FileCheck2, category: 'normal' },
  { label: 'VeriFlow', path: '/veriflow', icon: GitBranch, category: 'veriflow', badge: 'Rule Engine' },
  { label: 'Applications', path: '/applications', icon: FileText, category: 'normal' },
  { label: 'Audit Logs', path: '/audit', icon: ShieldCheck, category: 'normal' },
  { label: 'Settings', path: '/settings', icon: Settings, category: 'normal' },
];

export const Sidebar: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={`hidden md:flex flex-col border-r transition-all duration-300 z-20 ${
        isSidebarOpen ? 'w-64' : 'w-20'
      }`}
      style={{
        backgroundColor: 'var(--bg-sidebar)',
        borderColor: 'rgba(255,255,255,0.08)',
        color: '#f8fafc'
      }}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shrink-0 shadow-md shadow-blue-500/20">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          {isSidebarOpen && (
            <div className="flex flex-col">
              <span className="font-bold tracking-tight text-white leading-none">ScholarPath</span>
              <span className="text-[11px] text-blue-400 font-medium tracking-wide uppercase mt-1">Admin Portal</span>
            </div>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation items */}
      <nav className="flex-1 py-4 px-3 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isAmber = item.category === 'veriflow';

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all group relative ${
                  isActive
                    ? isAmber
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold'
                      : 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`w-5 h-5 shrink-0 transition-colors ${
                      isActive
                        ? isAmber
                          ? 'text-amber-400'
                          : 'text-blue-400'
                        : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                  {isSidebarOpen && (
                    <span className="ml-3 truncate">{item.label}</span>
                  )}
                  {isSidebarOpen && item.badge && (
                    <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">
                      {item.badge}
                    </span>
                  )}
                  {!isSidebarOpen && (
                    <div className="absolute left-full rounded-md px-2.5 py-1 ml-2 bg-slate-900 text-slate-100 text-xs shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap border border-slate-800">
                      {item.label}
                    </div>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer / Logout */}
      <div className="p-3 border-t border-slate-800">
        <NavLink
          to="/login"
          className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors w-full group relative"
        >
          <LogOut className="w-5 h-5 shrink-0 text-slate-400 group-hover:text-red-400" />
          {isSidebarOpen && <span className="ml-3">Logout</span>}
          {!isSidebarOpen && (
            <div className="absolute left-full rounded-md px-2.5 py-1 ml-2 bg-slate-900 text-red-400 text-xs shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap border border-slate-800">
              Logout
            </div>
          )}
        </NavLink>
      </div>
    </aside>
  );
};
