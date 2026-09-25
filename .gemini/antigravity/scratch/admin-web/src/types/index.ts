export type UserRole = 'ADMIN' | 'APPLICANT' | 'OFFICER';

export type SystemServiceStatus = 'Connected' | 'Unavailable' | 'Checking';

export interface SystemHealth {
  backend: SystemServiceStatus;
  sqlite: SystemServiceStatus;
  redis: SystemServiceStatus;
  websocket: SystemServiceStatus;
}

export interface NavItem {
  label: string;
  path: string;
  icon: string;
  badge?: string;
  category?: 'normal' | 'veriflow' | 'warning' | 'danger';
}

export interface AuthUser {
  id: string;
  applicationNumber: string;
  name: string;
  role: UserRole;
  department?: string;
}

export interface LoginRequest {
  applicationNumber: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  user: AuthUser;
}

export interface DashboardStats {
  totalScholarships: number;
  publishedScholarships: number;
  draftScholarships: number;
  activeApplications: number;
  activeVeriflowEvents: number;
  changesPublishedToday: number;
}

export type ActivityType =
  | 'SCHOLARSHIP_PUBLISHED'
  | 'FACT_VERSION_CREATED'
  | 'VERIFLOW_EVENT'
  | 'APPLICANT_NOTIFIED'
  | 'RECOVERY_DECISION';

export interface ActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  timestamp: string;
  badge?: string;
  category: 'normal' | 'veriflow' | 'warning' | 'danger';
}

export type ScholarshipStatus = 'draft' | 'published' | 'archived';

export type EducationLevel =
  | 'Undergraduate'
  | 'Postgraduate'
  | 'Doctoral'
  | 'Secondary'
  | 'Vocational';

export type ScholarshipCategory =
  | 'Merit-Based'
  | 'Need-Based'
  | 'Research'
  | 'Minority'
  | 'STEM'
  | 'Arts & Humanities';

export interface ScholarshipItem {
  id: string;
  title: string;
  provider: string;
  description: string;
  amount: number;
  deadline: string;
  status: ScholarshipStatus;
  educationLevels: EducationLevel[];
  categories: ScholarshipCategory[];
  regions: string[];
  eligibleRoles: string[];
  tags: string[];
  requiredDocuments: string[];
  updatedAt: string;
}

export interface ScholarshipFilterParams {
  search?: string;
  status?: ScholarshipStatus | 'all';
  educationLevel?: EducationLevel | 'all';
  category?: ScholarshipCategory | 'all';
  region?: string | 'all';
}

// Phase 5 Fact Models
export type FactType =
  | 'award_amount'
  | 'deadline'
  | 'eligibility'
  | 'required_documents'
  | 'education_level'
  | 'region'
  | 'application_fee';

export interface FactVersionItem {
  version: number;
  value: string;
  effectiveFrom: string;
  sourceNote: string;
  createdBy: string;
  createdAt: string;
}

export interface FactItem {
  id: string;
  scholarshipId: string;
  scholarshipTitle: string;
  factType: FactType;
  factKey: string;
  currentVersion: number;
  currentValue: string;
  effectiveFrom: string;
  sourceNote: string;
  createdBy: string;
  createdAt: string;
  versions: FactVersionItem[];
}

export interface CreateFactVersionPayload {
  newValue: string;
  effectiveFrom: string;
  sourceNote: string;
}

// Phase 6 & 7 VeriFlow Models
export type VeriflowClassification = 'cosmetic' | 'informational' | 'blocking';

export type VeriflowStatus =
  | 'detected'
  | 'classified'
  | 'notified'
  | 'resolved'
  | 'contested'
  | 'grace_period_requested';

export interface RecoveryDecisionItem {
  id: string;
  applicantId: string;
  applicantName: string;
  applicationNumber: string;
  decision: 'ACCEPT_REVISED_RULE' | 'REQUEST_GRACE_PERIOD' | 'CONTEST_CLASSIFICATION';
  status: 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED';
  timestamp: string;
}

export interface VeriflowEvent {
  id: string;
  scholarshipId: string;
  scholarshipTitle: string;
  factKey: string;
  oldVersion: number;
  newVersion: number;
  oldValue: string;
  newValue: string;
  classification: VeriflowClassification;
  affectedField: string;
  affectedApplicationsCount: number;
  status: VeriflowStatus;
  aiExplanation: string;
  recoveryDecisions: RecoveryDecisionItem[];
  createdAt: string;
}

export type VeriflowPipelineStep =
  | 'FACT_PUBLISHED'
  | 'CHANGE_DETECTED'
  | 'APPLICATIONS_IDENTIFIED'
  | 'CLASSIFIED'
  | 'APPLICANT_NOTIFIED'
  | 'RECOVERY_DECISION';

export interface DemoPublishResult {
  success: boolean;
  eventId: string;
  scholarshipTitle: string;
  factKey: string;
  oldVersion: number;
  newVersion: number;
  classification: VeriflowClassification;
  affectedApplicationsCount: number;
  message: string;
}

// Phase 8 Application Monitor & Audit Models
export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'ACTION_REQUIRED'
  | 'APPROVED'
  | 'REJECTED';

export interface ApplicationMonitorItem {
  id: string;
  applicationNumber: string;
  applicantId: string;
  applicantName: string;
  email: string;
  scholarshipId: string;
  scholarshipTitle: string;
  status: ApplicationStatus;
  activeFieldLocks: string[];
  veriflowStatus: VeriflowStatus | 'normal';
  currentFactSnapshotVersion: number;
  veriflowEvents: VeriflowEvent[];
  recoveryDecisions: RecoveryDecisionItem[];
  createdAt: string;
  updatedAt: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  eventType: string;
  actor: string;
  applicationId?: string;
  description: string;
  previousHash: string;
  entryHash: string;
  payload: Record<string, any>;
}

export interface AuditIntegrityResult {
  verified: boolean;
  brokenPosition: number | null;
  message: string;
  totalEntriesVerified: number;
}
