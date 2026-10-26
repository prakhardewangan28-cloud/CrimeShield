export type CaseStatus = 'open' | 'under_review' | 'closed';

export interface Case {
  id: number;
  case_code: string;
  title: string;
  description: string | null;
  location: string | null;
  status: CaseStatus;
  created_at: string | null;
  updated_at: string | null;
}

export interface CaseCreatePayload {
  case_code: string;
  title: string;
  description?: string;
  location?: string;
  status?: CaseStatus;
}

export interface CaseUpdatePayload {
  case_code?: string;
  title?: string;
  description?: string;
  location?: string;
  status?: CaseStatus;
}

export interface CaseStatistics {
  total: number;
  open: number;
  under_review: number;
  closed: number;
}

export type EvidenceProcessingStatus = 'pending' | 'processed' | 'flagged';

export interface Evidence {
  id: number;
  evidence_code: string;
  case_id: number;
  evidence_type: string;
  description: string | null;
  location_reference: string | null;
  person_reference: string | null;
  phone_reference: string | null;
  processing_status: EvidenceProcessingStatus;
  created_at: string | null;
}

export interface EvidenceCreatePayload {
  evidence_code: string;
  case_id: number;
  evidence_type: string;
  description?: string;
  location_reference?: string;
  person_reference?: string;
  phone_reference?: string;
  processing_status?: EvidenceProcessingStatus;
}

export interface EvidenceUpdatePayload {
  evidence_code?: string;
  evidence_type?: string;
  description?: string;
  location_reference?: string;
  person_reference?: string;
  phone_reference?: string;
  processing_status?: EvidenceProcessingStatus;
}

export interface EvidenceStatistics {
  total: number;
  by_type: Record<string, number>;
  by_status: {
    pending?: number;
    processed?: number;
    flagged?: number;
    [key: string]: number | undefined;
  };
}

export type ConnectionReviewStatus = 'pending' | 'confirmed_for_review' | 'dismissed';

export interface Connection {
  id: number;
  case_id_1: number;
  case_id_2: number;
  connection_type: string;
  connection_value: string;
  explanation: string;
  review_status: ConnectionReviewStatus;
  created_at: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
}

export interface ConnectionReviewPayload {
  review_status: ConnectionReviewStatus;
  review_notes?: string;
}

export interface ConnectionStatistics {
  total: number;
  pending: number;
  confirmed_for_review: number;
  dismissed: number;
}

export interface ConnectionGraphData {
  case_id: number;
  connected_cases: number[];
  connection_count: number;
  max_depth: number;
}

export interface AnalysisRunResult {
  status: string;
  evidence_count: number;
  connections_found: number;
  connections_created: number;
}

export interface SystemSummary {
  generated_at: string;
  cases: CaseStatistics;
  evidence: EvidenceStatistics;
  connections: {
    total: number;
    pending: number;
    confirmed_for_review: number;
    dismissed: number;
    by_type?: Record<string, number>;
    by_review_status?: Record<string, number>;
  };
}

export interface CaseReportInfo {
  case_id: number;
  case_code: string;
  title: string;
  evidence_count: number;
  connection_count: number;
  available_formats: string[];
}

export interface HealthResponse {
  service: string;
  status: string;
  version: string;
}

export interface ApiError {
  error: string;
  details?: string;
  message?: string;
}
