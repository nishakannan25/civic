import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scholarshipsService } from '../services/scholarships';
import { ScholarshipFilterParams, ScholarshipItem } from '../types';

export function useScholarshipsList(params?: ScholarshipFilterParams) {
  return useQuery({
    queryKey: ['scholarships', params],
    queryFn: () => scholarshipsService.getScholarships(params),
  });
}

export function useScholarship(id: string) {
  return useQuery({
    queryKey: ['scholarships', id],
    queryFn: () => scholarshipsService.getById(id),
    enabled: Boolean(id),
  });
}

export function useCreateScholarship() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<ScholarshipItem, 'id' | 'updatedAt' | 'status'>) =>
      scholarshipsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useUpdateScholarship() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ScholarshipItem> }) =>
      scholarshipsService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['scholarships', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function usePublishScholarship() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => scholarshipsService.publish(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useArchiveScholarship() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => scholarshipsService.archive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
