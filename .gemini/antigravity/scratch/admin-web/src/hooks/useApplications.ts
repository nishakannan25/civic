import { useQuery } from '@tanstack/react-query';
import { applicationsService } from '../services/applications';

export function useApplications(search?: string) {
  return useQuery({
    queryKey: ['applications', search],
    queryFn: () => applicationsService.getApplications(search),
  });
}

export function useApplication(id: string) {
  return useQuery({
    queryKey: ['applications', id],
    queryFn: () => applicationsService.getApplicationById(id),
    enabled: Boolean(id),
  });
}
