import { authFetch } from './auth';
import { FactItem, CreateFactVersionPayload } from '../types';

let mockFacts: FactItem[] = [
  {
    id: 'FCT-101',
    scholarshipId: 'SCH-001',
    scholarshipTitle: 'National Merit STEM Fellowship 2026',
    factType: 'award_amount',
    factKey: 'grant_disbursement_amount',
    currentVersion: 3,
    currentValue: '150000 INR per annum',
    effectiveFrom: '2026-09-01',
    sourceNote: 'Policy Gazette #2026/89B — Revised STEM stipend index',
    createdBy: 'ADM-2026-001',
    createdAt: '2026-09-24T10:30:00Z',
    versions: [
      {
        version: 1,
        value: '100000 INR per annum',
        effectiveFrom: '2025-01-01',
        sourceNote: 'Initial program foundation gazette',
        createdBy: 'ADM-2025-001',
        createdAt: '2025-01-01T09:00:00Z',
      },
      {
        version: 2,
        value: '125000 INR per annum',
        effectiveFrom: '2025-09-01',
        sourceNote: 'Mid-term inflation index amendment',
        createdBy: 'ADM-2025-004',
        createdAt: '2025-08-20T14:10:00Z',
      },
      {
        version: 3,
        value: '150000 INR per annum',
        effectiveFrom: '2026-09-01',
        sourceNote: 'Policy Gazette #2026/89B — Revised STEM stipend index',
        createdBy: 'ADM-2026-001',
        createdAt: '2026-09-24T10:30:00Z',
      },
    ],
  },
  {
    id: 'FCT-102',
    scholarshipId: 'SCH-001',
    scholarshipTitle: 'National Merit STEM Fellowship 2026',
    factType: 'required_documents',
    factKey: 'verifiable_document_schema',
    currentVersion: 2,
    currentValue: 'Income Certificate, Academic Transcript, National ID, Bank Statement',
    effectiveFrom: '2026-09-15',
    sourceNote: 'VeriFlow Rule #VF-104 — Mandatory bank account verification',
    createdBy: 'ADM-2026-001',
    createdAt: '2026-09-15T11:00:00Z',
    versions: [
      {
        version: 1,
        value: 'Income Certificate, Academic Transcript, National ID',
        effectiveFrom: '2026-01-01',
        sourceNote: 'Baseline document verification checklist',
        createdBy: 'ADM-2026-002',
        createdAt: '2026-01-01T10:00:00Z',
      },
      {
        version: 2,
        value: 'Income Certificate, Academic Transcript, National ID, Bank Statement',
        effectiveFrom: '2026-09-15',
        sourceNote: 'VeriFlow Rule #VF-104 — Mandatory bank account verification',
        createdBy: 'ADM-2026-001',
        createdAt: '2026-09-15T11:00:00Z',
      },
    ],
  },
  {
    id: 'FCT-103',
    scholarshipId: 'SCH-002',
    scholarshipTitle: 'Post-Matric Special Assistance Grant',
    factType: 'eligibility',
    factKey: 'family_income_ceiling',
    currentVersion: 1,
    currentValue: 'Annual Family Income <= 250000 INR',
    effectiveFrom: '2026-06-01',
    sourceNote: 'Social Welfare Department Order #SW-441',
    createdBy: 'ADM-2026-003',
    createdAt: '2026-06-01T08:00:00Z',
    versions: [
      {
        version: 1,
        value: 'Annual Family Income <= 250000 INR',
        effectiveFrom: '2026-06-01',
        sourceNote: 'Social Welfare Department Order #SW-441',
        createdBy: 'ADM-2026-003',
        createdAt: '2026-06-01T08:00:00Z',
      },
    ],
  },
  {
    id: 'FCT-104',
    scholarshipId: 'SCH-003',
    scholarshipTitle: 'Advanced AI & Quantum Computing Doctoral Grant',
    factType: 'application_fee',
    factKey: 'processing_fee_waiver',
    currentVersion: 1,
    currentValue: '0 INR (Full Waiver for Doctoral Researchers)',
    effectiveFrom: '2026-09-01',
    sourceNote: 'NSF Directive #NSF-2026-AI',
    createdBy: 'ADM-2026-001',
    createdAt: '2026-09-01T12:00:00Z',
    versions: [
      {
        version: 1,
        value: '0 INR (Full Waiver for Doctoral Researchers)',
        effectiveFrom: '2026-09-01',
        sourceNote: 'NSF Directive #NSF-2026-AI',
        createdBy: 'ADM-2026-001',
        createdAt: '2026-09-01T12:00:00Z',
      },
    ],
  },
];

export const factsService = {
  async getFacts(search?: string): Promise<FactItem[]> {
    try {
      const q = search ? `?search=${encodeURIComponent(search)}` : '';
      return await authFetch<FactItem[]>(`/api/facts${q}`);
    } catch {
      let result = [...mockFacts];
      if (search) {
        const query = search.toLowerCase();
        result = result.filter(
          (f) =>
            f.scholarshipTitle.toLowerCase().includes(query) ||
            f.factType.toLowerCase().includes(query) ||
            f.factKey.toLowerCase().includes(query) ||
            f.currentValue.toLowerCase().includes(query)
        );
      }
      return result;
    }
  },

  async getFactById(id: string): Promise<FactItem | null> {
    try {
      return await authFetch<FactItem>(`/api/facts/${id}`);
    } catch {
      return mockFacts.find((f) => f.id === id) || null;
    }
  },

  async createNewVersion(id: string, payload: CreateFactVersionPayload): Promise<FactItem> {
    try {
      return await authFetch<FactItem>(`/api/facts/${id}/versions`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    } catch {
      const idx = mockFacts.findIndex((f) => f.id === id);
      if (idx === -1) throw new Error('Fact not found');

      const existing = mockFacts[idx];
      const newVersionNumber = existing.currentVersion + 1;

      const newVersionObj = {
        version: newVersionNumber,
        value: payload.newValue,
        effectiveFrom: payload.effectiveFrom,
        sourceNote: payload.sourceNote,
        createdBy: 'ADM-2026-001',
        createdAt: new Date().toISOString(),
      };

      const updatedFact: FactItem = {
        ...existing,
        currentVersion: newVersionNumber,
        currentValue: payload.newValue,
        effectiveFrom: payload.effectiveFrom,
        sourceNote: payload.sourceNote,
        createdBy: 'ADM-2026-001',
        createdAt: new Date().toISOString(),
        // NEVER overwrite old versions array - append new version
        versions: [...existing.versions, newVersionObj],
      };

      mockFacts[idx] = updatedFact;
      return updatedFact;
    }
  },
};
