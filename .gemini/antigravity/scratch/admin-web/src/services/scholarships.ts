import { authFetch } from './auth';
import { ScholarshipItem, ScholarshipFilterParams } from '../types';

// In-memory dev storage seed to allow seamless CRUD testing even if backend is offline
let mockScholarships: ScholarshipItem[] = [
  {
    id: 'SCH-001',
    title: 'National Merit STEM Fellowship 2026',
    provider: 'Ministry of Higher Education',
    description: 'Premier merit-based financial aid for high-performing undergraduate & postgraduate STEM students.',
    amount: 150000,
    deadline: '2026-11-30',
    status: 'published',
    educationLevels: ['Undergraduate', 'Postgraduate'],
    categories: ['Merit-Based', 'STEM'],
    regions: ['National', 'State-Level'],
    eligibleRoles: ['STUDENT', 'RESEARCHER'],
    tags: ['Merit', 'STEM', 'Fellowship'],
    requiredDocuments: ['Income Certificate', 'Academic Transcript', 'National ID'],
    updatedAt: '2026-09-24T10:30:00Z',
  },
  {
    id: 'SCH-002',
    title: 'Post-Matric Special Assistance Grant',
    provider: 'Social Welfare Department',
    description: 'Financial support targeted for secondary and vocational school graduates from marginalized communities.',
    amount: 75000,
    deadline: '2026-10-15',
    status: 'published',
    educationLevels: ['Secondary', 'Vocational'],
    categories: ['Need-Based', 'Minority'],
    regions: ['Regional'],
    eligibleRoles: ['STUDENT'],
    tags: ['Need-Based', 'Minority'],
    requiredDocuments: ['Caste Certificate', 'Income Certificate'],
    updatedAt: '2026-09-22T14:15:00Z',
  },
  {
    id: 'SCH-003',
    title: 'Advanced AI & Quantum Computing Doctoral Grant',
    provider: 'National Science Foundation',
    description: 'Specialized grant for doctoral candidates investigating deep learning architectures & quantum hardware.',
    amount: 300000,
    deadline: '2026-12-01',
    status: 'draft',
    educationLevels: ['Doctoral'],
    categories: ['Research', 'STEM'],
    regions: ['National'],
    eligibleRoles: ['RESEARCHER', 'DOCTORAL_FELLOW'],
    tags: ['AI', 'Quantum', 'Research'],
    requiredDocuments: ['Research Proposal', 'Publication Record', 'Recommendation Letter'],
    updatedAt: '2026-09-25T09:00:00Z',
  },
  {
    id: 'SCH-004',
    title: 'Arts & Cultural Heritage Excellence Award',
    provider: 'Department of Cultural Affairs',
    description: 'Scholarship supporting classical art forms, literature preservation, and historical research.',
    amount: 90000,
    deadline: '2026-08-30',
    status: 'archived',
    educationLevels: ['Undergraduate', 'Postgraduate'],
    categories: ['Arts & Humanities'],
    regions: ['State-Level'],
    eligibleRoles: ['STUDENT', 'ARTISAN'],
    tags: ['Arts', 'Culture', 'Heritage'],
    requiredDocuments: ['Portfolio', 'Academic Transcript'],
    updatedAt: '2026-08-31T18:00:00Z',
  },
];

export const scholarshipsService = {
  async getScholarships(params?: ScholarshipFilterParams): Promise<ScholarshipItem[]> {
    try {
      const query = new URLSearchParams();
      if (params?.search) query.append('search', params.search);
      if (params?.status && params.status !== 'all') query.append('status', params.status);
      if (params?.educationLevel && params.educationLevel !== 'all') query.append('educationLevel', params.educationLevel);
      if (params?.category && params.category !== 'all') query.append('category', params.category);
      if (params?.region && params.region !== 'all') query.append('region', params.region);

      return await authFetch<ScholarshipItem[]>(`/api/scholarships?${query.toString()}`);
    } catch {
      // Development fallback filter logic
      let result = [...mockScholarships];

      if (params?.search) {
        const q = params.search.toLowerCase();
        result = result.filter(
          (s) =>
            s.title.toLowerCase().includes(q) ||
            s.provider.toLowerCase().includes(q) ||
            s.categories.some((c) => c.toLowerCase().includes(q)) ||
            s.tags.some((t) => t.toLowerCase().includes(q))
        );
      }

      if (params?.status && params.status !== 'all') {
        result = result.filter((s) => s.status === params.status);
      }

      if (params?.educationLevel && params.educationLevel !== 'all') {
        const targetLvl = params.educationLevel;
        result = result.filter((s) => s.educationLevels.includes(targetLvl as any));
      }

      if (params?.category && params.category !== 'all') {
        const targetCat = params.category;
        result = result.filter((s) => s.categories.includes(targetCat as any));
      }

      if (params?.region && params.region !== 'all') {
        result = result.filter((s) => s.regions.includes(params.region as string));
      }

      return result;
    }
  },

  async getById(id: string): Promise<ScholarshipItem | null> {
    try {
      return await authFetch<ScholarshipItem>(`/api/scholarships/${id}`);
    } catch {
      return mockScholarships.find((s) => s.id === id) || null;
    }
  },

  async create(data: Omit<ScholarshipItem, 'id' | 'updatedAt' | 'status'>): Promise<ScholarshipItem> {
    try {
      return await authFetch<ScholarshipItem>('/api/scholarships', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch {
      const newItem: ScholarshipItem = {
        ...data,
        id: `SCH-${String(mockScholarships.length + 1).padStart(3, '0')}`,
        status: 'draft',
        updatedAt: new Date().toISOString(),
      };
      mockScholarships.unshift(newItem);
      return newItem;
    }
  },

  async update(id: string, data: Partial<ScholarshipItem>): Promise<ScholarshipItem> {
    try {
      return await authFetch<ScholarshipItem>(`/api/scholarships/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    } catch {
      const idx = mockScholarships.findIndex((s) => s.id === id);
      if (idx === -1) throw new Error('Scholarship not found');
      mockScholarships[idx] = {
        ...mockScholarships[idx],
        ...data,
        updatedAt: new Date().toISOString(),
      };
      return mockScholarships[idx];
    }
  },

  async publish(id: string): Promise<ScholarshipItem> {
    try {
      return await authFetch<ScholarshipItem>(`/api/scholarships/${id}/publish`, {
        method: 'POST',
      });
    } catch {
      return this.update(id, { status: 'published' });
    }
  },

  async archive(id: string): Promise<ScholarshipItem> {
    try {
      return await authFetch<ScholarshipItem>(`/api/scholarships/${id}/archive`, {
        method: 'POST',
      });
    } catch {
      return this.update(id, { status: 'archived' });
    }
  },
};
