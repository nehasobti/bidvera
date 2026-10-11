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
  section_number?: number;
  title: string;
  description: string;
  mapped_requirements: string[];
  target_pages?: number;
  word_limit?: number;
  status?: string;
}

export interface DraftedSection {
  section_id: string;
  title: string;
  content: string;
  mapped_requirements: string[];
  word_count?: number;
  status?: string;
}

export interface PriceLineItem {
  role_key: string;
  role_title: string;
  hours: number;
  days: number;
  hourly_rate: number;
  daily_rate: number;
  base_cost: number;
  margin_amount: number;
  line_total: number;
}

export interface PriceSheet {
  currency: string;
  margin_percentage: number;
  lines?: PriceLineItem[];
  line_items?: PriceLineItem[];
  total_hours: number;
  total_days?: number;
  total_person_days?: number;
  subtotal_base_cost: number;
  total_margin: number;
  grand_total?: number;
  total_price?: number;
  blended_hourly_rate: number;
  blended_daily_rate: number;
  assumptions?: string[];
}

export interface CommercialPricing {
  effort?: {
    total_hours: number;
    total_days: number;
    role_summary: Record<string, number>;
  };
  price_sheet?: PriceSheet;
  currency: string;
  total_price: number;
  total_days: number;
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
  sections?: DraftedSection[];
  pricing?: CommercialPricing;
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
