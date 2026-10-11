export interface TenderSummary {
  id: string;
  title: string;
  buyer: string;
  country: string;
  category: string;
  deadline: string;
  estimated_value: number;
  currency: string;
  summary: string;
  fit_score?: number;
  fit_reasons?: string[];
  documents?: {
    id: string;
    filename: string;
    path: string;
    description: string;
  }[];
}

export interface Requirement {
  id: string;
  text: string;
  type: string;
  weight: string;
  section: string;
  page_ref: string;
  category: string;
}

export interface CriterionResult {
  name: string;
  status: "pass" | "fail" | "warn";
  details: string;
  required: string;
  actual: string;
}

export interface EligibilityResult {
  recommendation: "bid" | "no-bid" | "review";
  reasons: string[];
  criteria_results: CriterionResult[];
}

export interface OutlineSection {
  id: string;
  title: string;
  description: string;
  mapped_requirements: string[];
  target_pages?: number;
  status?: string;
}

export interface BidDecision {
  decision: "bid" | "no-bid";
  comment?: string;
  who: string;
  timestamp?: string;
}

export interface BidMetadata {
  id?: string;
  tender_id?: string;
  title?: string;
  buyer?: string;
  country?: string;
  category?: string;
  deadline?: string;
  summary?: string;
  status?: string;
  eligibility_criteria?: string[];
}

export interface BidRecord {
  bid_id: string;
  status: string;
  tender_id?: string;
  bid?: BidMetadata;
  documents?: any[];
  documents_count?: number;
  requirements?: Requirement[];
  requirements_count?: number;
  eligibility?: EligibilityResult;
  outline?: OutlineSection[];
  decisions?: BidDecision[];
  is_waiting_for_approval?: boolean;
  pending_checkpoint?: any;
  error?: string | null;
}

export interface ApprovalTask {
  bid_id: string;
  status: string;
  tender_id?: string;
  title?: string;
  buyer?: string;
  recommendation?: string;
  reasons?: string[];
  checkpoint?: string;
  interrupt_payload?: any;
  requirements_count?: number;
}
