import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboard';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => dashboardService.getStats(),
    refetchInterval: 15000,
  });
}

export function useDashboardActivities() {
  return useQuery({
    queryKey: ['dashboard', 'activities'],
    queryFn: () => dashboardService.getActivities(),
    refetchInterval: 10000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['dashboard', 'health'],
    queryFn: () => dashboardService.getSystemHealth(),
    refetchInterval: 5000,
  });
}
