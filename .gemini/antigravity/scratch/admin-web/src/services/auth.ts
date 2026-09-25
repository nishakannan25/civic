import { LoginRequest, AuthResponse, AuthUser } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// In-memory access token storage (never saved in localStorage / sessionStorage)
let memoryAccessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  memoryAccessToken = token;
};

export const getAccessToken = () => memoryAccessToken;

export async function authFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string> || {}),
  };

  if (memoryAccessToken) {
    headers['Authorization'] = `Bearer ${memoryAccessToken}`;
  }

  // Include credentials for httpOnly cookies (refresh token)
  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh')) {
    // Attempt silent token refresh
    try {
      const refreshed = await authService.refreshToken();
      if (refreshed?.accessToken) {
        headers['Authorization'] = `Bearer ${refreshed.accessToken}`;
        const retryResponse = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
        if (retryResponse.ok) {
          return retryResponse.json();
        }
      }
    } catch {
      setAccessToken(null);
    }
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ message: response.statusText }));
    const error = new Error(errorBody.message || errorBody.detail || `Request failed with status ${response.status}`);
    (error as any).status = response.status;
    throw error;
  }

  return response.json();
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // For Phase 2 standalone development / mock server fallback
    if (!credentials.applicationNumber || !credentials.password) {
      throw new Error('Application Number and Password are required');
    }

    try {
      const res = await authFetch<AuthResponse>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
      setAccessToken(res.accessToken);
      return res;
    } catch (err: any) {
      // Development mock fallback if backend is standby
      if (err.message?.includes('Failed to fetch') || err.status === 404 || err.status === 502) {
        if (credentials.password === 'wrong') {
          throw new Error('Invalid Application Number or Password');
        }
        if (credentials.applicationNumber.toLowerCase().includes('user')) {
          // Non-admin user test case
          const mockNonAdminResponse: AuthResponse = {
            accessToken: 'mock-jwt-token-non-admin',
            user: {
              id: 'USR-999',
              applicationNumber: credentials.applicationNumber,
              name: 'John Student',
              role: 'APPLICANT',
            }
          };
          setAccessToken(mockNonAdminResponse.accessToken);
          return mockNonAdminResponse;
        }

        // Default Admin login success
        const mockAdminResponse: AuthResponse = {
          accessToken: 'mock-jwt-token-admin-12345',
          user: {
            id: 'ADM-001',
            applicationNumber: credentials.applicationNumber,
            name: 'Senior Admin Officer',
            role: 'ADMIN',
            department: 'Scholarship Directorate',
          },
        };
        setAccessToken(mockAdminResponse.accessToken);
        return mockAdminResponse;
      }
      throw err;
    }
  },

  async logout(): Promise<void> {
    try {
      await authFetch('/api/auth/logout', { method: 'POST' });
    } catch {
      // Ignore logout backend errors
    } finally {
      setAccessToken(null);
    }
  },

  async refreshToken(): Promise<AuthResponse | null> {
    try {
      const res = await authFetch<AuthResponse>('/api/auth/refresh', { method: 'POST' });
      setAccessToken(res.accessToken);
      return res;
    } catch {
      setAccessToken(null);
      return null;
    }
  },

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const user = await authFetch<AuthUser>('/api/auth/me');
      return user;
    } catch {
      return null;
    }
  },
};
