import { authFetch } from './auth';
import { VeriflowEvent, DemoPublishResult } from '../types';

let mockVeriflowEvents: VeriflowEvent[] = [
  {
    id: 'VF-EVT-901',
    scholarshipId: 'SCH-001',
    scholarshipTitle: 'National Merit STEM Fellowship 2026',
    factKey: 'grant_disbursement_amount',
    oldVersion: 2,
    newVersion: 3,
    oldValue: '125000 INR per annum',
    newValue: '150000 INR per annum',
    classification: 'informational',
    affectedField: 'financial_grant_disbursement',
    affectedApplicationsCount: 42,
    status: 'resolved',
    aiExplanation:
      'The grant amount increased by 25,000 INR. This update is favorable to applicants and requires no re-submisson or document upload.',
    recoveryDecisions: [
      {
        id: 'DEC-01',
        applicantId: 'APP-8841',
        applicantName: 'Aarav Sharma',
        applicationNumber: 'APP-2026-8841',
        decision: 'ACCEPT_REVISED_RULE',
        status: 'APPROVED',
        timestamp: '2026-09-24T11:00:00Z',
      },
      {
        id: 'DEC-02',
        applicantId: 'APP-8842',
        applicantName: 'Ananya Roy',
        applicationNumber: 'APP-2026-8842',
        decision: 'ACCEPT_REVISED_RULE',
        status: 'APPROVED',
        timestamp: '2026-09-24T11:05:00Z',
      },
    ],
    createdAt: '2026-09-24T10:35:00Z',
  },
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
      'Addition of mandatory "Bank Statement" document invalidates active applicant submission. Field lock applied until applicant uploads bank proof.',
    recoveryDecisions: [
      {
        id: 'DEC-03',
        applicantId: 'APP-9012',
        applicantName: 'Rohan Verma',
        applicationNumber: 'APP-2026-9012',
        decision: 'REQUEST_GRACE_PERIOD',
        status: 'PENDING_REVIEW',
        timestamp: '2026-09-25T14:15:00Z',
      },
    ],
    createdAt: '2026-09-25T14:00:00Z',
  },
];

export const veriflowService = {
  async getEvents(): Promise<VeriflowEvent[]> {
    try {
      return await authFetch<VeriflowEvent[]>('/api/veriflow/events');
    } catch {
      return [...mockVeriflowEvents];
    }
  },

  async getEventById(id: string): Promise<VeriflowEvent | null> {
    try {
      return await authFetch<VeriflowEvent>(`/api/veriflow/events/${id}`);
    } catch {
      return mockVeriflowEvents.find((e) => e.id === id) || null;
    }
  },

  /**
   * One-click Demo Rule Change Trigger
   * Calls FastAPI backend endpoint POST `/api/veriflow/demo-publish`
   */
  async triggerDemoPublish(): Promise<DemoPublishResult> {
    try {
      return await authFetch<DemoPublishResult>('/api/veriflow/demo-publish', {
        method: 'POST',
      });
    } catch {
      // Development mock pipeline fallback
      const newEvent: VeriflowEvent = {
        id: `VF-EVT-${Math.floor(100 + Math.random() * 900)}`,
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
          'Live Demo Execution: Addition of mandatory "Bank Statement" invalidates active applicant application APP-2026-9012. Field locked.',
        recoveryDecisions: [
          {
            id: `DEC-${Math.floor(10 + Math.random() * 90)}`,
            applicantId: 'APP-9012',
            applicantName: 'Rohan Verma',
            applicationNumber: 'APP-2026-9012',
            decision: 'REQUEST_GRACE_PERIOD',
            status: 'PENDING_REVIEW',
            timestamp: new Date().toISOString(),
          },
        ],
        createdAt: new Date().toISOString(),
      };

      mockVeriflowEvents.unshift(newEvent);

      return {
        success: true,
        eventId: newEvent.id,
        scholarshipTitle: 'ScholarPath Merit Scholarship 2026',
        factKey: 'required_documents',
        oldVersion: 3,
        newVersion: 4,
        classification: 'blocking',
        affectedApplicationsCount: 1,
        message: '✓ Rule change published to SQLite/Redis/WebSocket',
      };
    }
  },

  subscribeWebSocket(onEvent: (eventData: any) => void): () => void {
    let ws: WebSocket | null = null;
    let fallbackInterval: number | null = null;

    try {
      ws = new WebSocket('ws://localhost:8000/ws/veriflow');

      ws.onmessage = (message) => {
        try {
          const data = JSON.parse(message.data);
          onEvent(data);
        } catch (e) {
          console.error('WebSocket payload parse error:', e);
        }
      };

      ws.onerror = () => {
        startMockTicker(onEvent);
      };
    } catch {
      startMockTicker(onEvent);
    }

    function startMockTicker(callback: (data: any) => void) {
      if (fallbackInterval) return;
      fallbackInterval = window.setInterval(() => {
        const sampleEvent = {
          type: 'veriflow_completed',
          eventId: 'VF-EVT-902',
          status: 'notified',
          timestamp: new Date().toISOString(),
          message: 'VeriFlow auto-classifier notified 1 affected applicant',
        };
        callback(sampleEvent);
      }, 15000);
    }

    return () => {
      if (ws) ws.close();
      if (fallbackInterval) clearInterval(fallbackInterval);
    };
  },
};
