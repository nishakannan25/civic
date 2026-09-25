import { create } from 'zustand';

interface UIState {
  isSidebarOpen: boolean;
  isMobileDrawerOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  toggleMobileDrawer: () => void;
  setMobileDrawer: (open: boolean) => void;
  toggleTheme: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  isMobileDrawerOpen: false,
  theme: (localStorage.getItem('scholarpath_theme') as 'light' | 'dark') || 'light',
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  toggleMobileDrawer: () => set((state) => ({ isMobileDrawerOpen: !state.isMobileDrawerOpen })),
  setMobileDrawer: (open: boolean) => set({ isMobileDrawerOpen: open }),
  toggleTheme: () => set((state) => {
    const nextTheme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('scholarpath_theme', nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    return { theme: nextTheme };
  }),
}));
