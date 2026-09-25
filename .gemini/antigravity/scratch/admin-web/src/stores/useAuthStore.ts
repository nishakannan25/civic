import { create } from 'zustand';
import { AuthUser, LoginRequest } from '../types';
import { authService, setAccessToken } from '../services/auth';

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  initializeAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true, // start loading session
  error: null,

  login: async (credentials: LoginRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login(credentials);
      
      // Enforce ADMIN role check
      if (response.user.role !== 'ADMIN') {
        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: 'Access Denied: Administrative privileges required.',
        });
        return;
      }

      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (err: any) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: err.message || 'Login failed. Please check credentials.',
      });
      throw err;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    await authService.logout();
    setAccessToken(null);
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  },

  initializeAuth: async () => {
    set({ isLoading: true });
    try {
      // Attempt silent refresh via httpOnly cookies
      const refreshed = await authService.refreshToken();
      if (refreshed?.user) {
        set({
          user: refreshed.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
        return;
      }
    } catch {
      // Silent refresh failed
    }
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  clearError: () => set({ error: null }),
}));
