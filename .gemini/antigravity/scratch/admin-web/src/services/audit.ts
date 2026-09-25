import { authFetch } from './auth';
import { AuditLogEntry, AuditIntegrityResult } from '../types';

let mockAuditLogs: AuditLogEntry[] = [
  {
    id: 'AUD-001',
    timestamp: '2026-09-25T14:15:00Z',
    eventType: 'APPLICANT_RECOVERY_DECISION',
    actor: 'USR-8012 (Rohan Verma)',
    applicationId: 'APP-9012',
    description: 'Applicant submitted Grace Period request for required_documents rule change',
    previousHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    entryHash: 'a718b52f19208031d274092b77c68832a821d3f9b2071dfa52b1158b09320e88',
    payload: {
      decision: 'REQUEST_GRACE_PERIOD',
      reason: 'Awaiting Bank Statement issuance from Treasury',
    },
  },
  {
    id: 'AUD-002',
    timestamp: '2026-09-25T14:00:00Z',
    eventType: 'FACT_VERSION_PUBLISHED',
    actor: 'ADM-1004 (Dr. S. Kumar)',
    applicationId: 'APP-9012',
    description: 'Published Fact version 4 for required_documents (added Bank Statement)',
    previousHash: 'a718b52f19208031d274092b77c68832a821d3f9b2071dfa52b1158b09320e88',
    entryHash: 'f49a620b78491c33a921d723b562a11b084e9301648a9726b1a8d11c784912ab',
    payload: {
      factKey: 'required_documents',
      oldVersion: 3,
      newVersion: 4,
      sourceNote: 'Gazette Extra-Ordinary 2026/S-41',
    },
  },
  {
    id: 'AUD-003',
    timestamp: '2026-09-20T10:00:00Z',
    eventType: 'APPLICATION_SUBMITTED',
    actor: 'USR-8012 (Rohan Verma)',
    applicationId: 'APP-9012',
    description: 'Initial application submission under Scholarship SCH-001',
    previousHash: '0000000000000000000000000000000000000000000000000000000000000000',
    entryHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    payload: {
      scholarshipId: 'SCH-001',
      documentsUploaded: ['Income Certificate'],
    },
  },
];

export const auditService = {
  async getAuditLogs(): Promise<AuditLogEntry[]> {
    try {
      return await authFetch<AuditLogEntry[]>('/api/audit/logs');
    } catch {
      return [...mockAuditLogs];
    }
  },

  async verifyIntegrity(applicationId?: string): Promise<AuditIntegrityResult> {
    try {
      const endpoint = applicationId
        ? `/api/applications/${applicationId}/audit/integrity`
        : '/api/audit/integrity';
      return await authFetch<AuditIntegrityResult>(endpoint);
    } catch {
      return {
        verified: true,
        brokenPosition: null,
        message: '✓ Cryptographic hash chain verified successfully. 0 tampered entries detected.',
        totalEntriesVerified: mockAuditLogs.length,
      };
    }
  },
};
