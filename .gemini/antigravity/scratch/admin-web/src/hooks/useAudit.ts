import { useQuery, useMutation } from '@tanstack/react-query';
import { auditService } from '../services/audit';

export function useAuditLogs() {
  return useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => auditService.getAuditLogs(),
  });
}

export function useVerifyAuditIntegrity() {
  return useMutation({
    mutationFn: (applicationId?: string) => auditService.verifyIntegrity(applicationId),
  });
}
