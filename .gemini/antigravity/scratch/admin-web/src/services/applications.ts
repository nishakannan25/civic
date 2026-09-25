import { authFetch } from './auth';
import { ApplicationMonitorItem } from '../types';

let mockApplications: ApplicationMonitorItem[] = [
  {
    id: 'APP-9012',
    applicationNumber: 'APP-2026-9012',
    applicantId: 'USR-8012',
    applicantName: 'Rohan Verma',
    email: 'rohan.verma@example.gov.in',
    scholarshipId: 'SCH-001',
    scholarshipTitle: 'ScholarPath Merit Scholarship 2026',
    status: 'ACTION_REQUIRED',
    activeFieldLocks: ['required_documents'],
    veriflowStatus: 'notified',
    currentFactSnapshotVersion: 3,
    veriflowEvents: [
      {
        id: 'VF-EVT-902',
        scholarshipId: 'SCH-001',
        scholarshipTitle: 'ScholarPath Merit Scholarship 2026',
        factKey: 'required_documents',
        oldVersion: 3,
        newVersion: 4,
        oldValue: 'Income Certificate',
        newValue: 'Income Certificate, Bank Statement',
        classification: 'blocking',
        affectedField: 'required_documents',
        affectedApplicationsCount: 1,
        status: 'notified',
        aiExplanation:
          'Addition of mandatory "Bank Statement" invalidates application APP-2026-9012. Field lock applied.',
        recoveryDecisions: [],
        createdAt: '2026-09-25T14:00:00Z',
      },
    ],
    recoveryDecisions: [
      {
        id: 'DEC-03',
        applicantId: 'USR-8012',
        applicantName: 'Rohan Verma',
        applicationNumber: 'APP-2026-9012',
        decision: 'REQUEST_GRACE_PERIOD',
        status: 'PENDING_REVIEW',
        timestamp: '2026-09-25T14:15:00Z',
      },
    ],
    createdAt: '2026-09-20T10:00:00Z',
    updatedAt: '2026-09-25T14:15:00Z',
  },
  {
    id: 'APP-8841',
    applicationNumber: 'APP-2026-8841',
    applicantId: 'USR-7841',
    applicantName: 'Aarav Sharma',
    email: 'aarav.sharma@example.gov.in',
    scholarshipId: 'SCH-001',
    scholarshipTitle: 'National Merit STEM Fellowship 2026',
    status: 'APPROVED',
    activeFieldLocks: [],
    veriflowStatus: 'resolved',
    currentFactSnapshotVersion: 3,
    veriflowEvents: [],
    recoveryDecisions: [],
    createdAt: '2026-09-18T09:30:00Z',
    updatedAt: '2026-09-24T11:00:00Z',
  },
  {
    id: 'APP-8842',
    applicationNumber: 'APP-2026-8842',
    applicantId: 'USR-7842',
    applicantName: 'Ananya Roy',
    email: 'ananya.roy@example.gov.in',
    scholarshipId: 'SCH-002',
    scholarshipTitle: 'Post-Matric Special Assistance Grant',
    status: 'UNDER_REVIEW',
    activeFieldLocks: [],
    veriflowStatus: 'normal',
    currentFactSnapshotVersion: 2,
    veriflowEvents: [],
    recoveryDecisions: [],
    createdAt: '2026-09-22T11:15:00Z',
    updatedAt: '2026-09-25T12:00:00Z',
  },
];

export const applicationsService = {
  async getApplications(search?: string): Promise<ApplicationMonitorItem[]> {
    try {
      const query = search ? `?search=${encodeURIComponent(search)}` : '';
      return await authFetch<ApplicationMonitorItem[]>(`/api/applications${query}`);
    } catch {
      if (!search) return [...mockApplications];
      const q = search.toLowerCase();
      return mockApplications.filter(
        (app) =>
          app.applicationNumber.toLowerCase().includes(q) ||
          app.applicantName.toLowerCase().includes(q) ||
          app.scholarshipTitle.toLowerCase().includes(q)
      );
    }
  },

  async getApplicationById(id: string): Promise<ApplicationMonitorItem | null> {
    try {
      return await authFetch<ApplicationMonitorItem>(`/api/applications/${id}`);
    } catch {
      return mockApplications.find((app) => app.id === id || app.applicationNumber === id) || null;
    }
  },
};
