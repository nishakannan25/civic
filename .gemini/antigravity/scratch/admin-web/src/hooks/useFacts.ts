import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { factsService } from '../services/facts';
import { CreateFactVersionPayload } from '../types';

export function useFactsList(search?: string) {
  return useQuery({
    queryKey: ['facts', search],
    queryFn: () => factsService.getFacts(search),
  });
}

export function useFact(id: string) {
  return useQuery({
    queryKey: ['facts', id],
    queryFn: () => factsService.getFactById(id),
    enabled: Boolean(id),
  });
}

export function useCreateFactVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CreateFactVersionPayload }) =>
      factsService.createNewVersion(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['facts'] });
      queryClient.invalidateQueries({ queryKey: ['facts', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
