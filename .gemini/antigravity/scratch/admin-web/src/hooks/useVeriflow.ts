import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { veriflowService } from '../services/veriflow';

export function useVeriflowEvents() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const unsubscribe = veriflowService.subscribeWebSocket((eventData) => {
      queryClient.invalidateQueries({ queryKey: ['veriflow-events'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['facts'] });
    });

    return () => unsubscribe();
  }, [queryClient]);

  return useQuery({
    queryKey: ['veriflow-events'],
    queryFn: () => veriflowService.getEvents(),
  });
}

export function useVeriflowEvent(id: string) {
  return useQuery({
    queryKey: ['veriflow-events', id],
    queryFn: () => veriflowService.getEventById(id),
    enabled: Boolean(id),
  });
}

export function useTriggerDemoPublish() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => veriflowService.triggerDemoPublish(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['veriflow-events'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['facts'] });
    },
  });
}
