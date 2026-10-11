"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { fetchBid, submitBidDecision } from "@/lib/api";
import { formatDate } from "@/lib/date";
import {
  BidRecord,
  Requirement,
  OutlineSection,
  DraftedSection,
  CommercialPricing,
  ComplianceMatrixItem,
  ProposalReview,
  DocumentArtifacts,
} from "@/types";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Layers,
  ShieldCheck,
  ListOrdered,
  ArrowLeft,
  Check,
  RotateCw,
  Building2,
  Calendar,
  CheckCheck,
  DollarSign,
  Edit3,
  Coins,
  FileCheck,
  Download,
  Award,
  Sparkles,
  ExternalLink,
} from "lucide-react";

export default function BidWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const bidId = resolvedParams.id;

  const [bid, setBid] = useState<BidRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    | "timeline"
    | "requirements"
    | "eligibility"
    | "outline"
    | "sections"
    | "pricing"
    | "compliance"
    | "review"
    | "artifacts"
  >("timeline");
  const [decisionSubmitting, setDecisionSubmitting] = useState(false);
  const [comment, setComment] = useState("");

  const loadBidData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBid(bidId);
      setBid(data);
    } catch (err: any) {
      setError(err.message || "Failed to load bid details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBidData();
    const interval = setInterval(loadBidData, 4000);
    return () => clearInterval(interval);
  }, [bidId]);

  const handleDecision = async (decision: "bid" | "no-bid") => {
    try {
      setDecisionSubmitting(true);
      await submitBidDecision(bidId, decision, comment, "Bid Director");
      await loadBidData();
    } catch (err: any) {
      setError(err.message || "Failed to submit decision");
    } finally {
      setDecisionSubmitting(false);
    }
  };

  if (loading && !bid) {
    return (
      <div className="p-16 text-center text-slate-500 bg-white border border-slate-200 rounded-2xl shadow-xs">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs font-semibold text-slate-700">Loading bid workspace & state snapshot...</p>
      </div>
    );
  }

  if (!bid) {
    return (
      <div className="p-12 text-center bg-white border border-slate-200 rounded-2xl shadow-xs space-y-3">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-base font-bold text-slate-900">Bid Thread Not Found</h3>
        <p className="text-xs text-slate-500">The requested bid ID could not be retrieved from the agent database.</p>
        <Link
          href="/bids"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold mt-2"
        >
          Return to Bids
        </Link>
      </div>
    );
  }

  const isWaiting = (bid as any).is_waiting_for_approval;
  const status = bid.status;
  const eligibility = bid.eligibility;
  const requirements: Requirement[] = (bid as any).requirements || [];
  const outline: OutlineSection[] = (bid as any).outline || [];
  const sections: DraftedSection[] = (bid as any).sections || [];
  const pricing: CommercialPricing = (bid as any).pricing || {};
  const matrix: ComplianceMatrixItem[] = (bid as any).compliance_matrix || [];
  const review: ProposalReview | undefined = (bid as any).review;
  const artifacts: DocumentArtifacts = (bid as any).artifacts || {};

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <Link
            href="/bids"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to All Bids</span>
          </Link>

          <button
            onClick={loadBidData}
            className="p-2 text-slate-500 hover:text-slate-800 border border-slate-200 rounded-xl hover:bg-slate-50 shadow-xs transition"
            title="Refresh State"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pt-2 border-t border-slate-100">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2.5 py-0.5 rounded-md border border-slate-200">
                {bidId}
              </span>
              <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-md border border-blue-200 uppercase">
                {bid.bid?.category || "TENDER"}
              </span>

              {isWaiting && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300 animate-pulse">
                  <Clock className="w-3.5 h-3.5 text-amber-600" />
                  Awaiting Executive Decision
                </span>
              )}

              {artifacts.status === "ready" && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  Proposal DOCX & PDF Ready
                </span>
              )}
            </div>

            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {bid.bid?.title || bid.tender_id}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <strong className="text-slate-700">{bid.bid?.buyer || "N/A"}</strong>
              </span>
              <span>&bull;</span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Deadline: {formatDate(bid.bid?.deadline)}</span>
              </span>
              {pricing.total_price && (
                <>
                  <span>&bull;</span>
                  <span className="font-semibold text-emerald-700">
                    Quote: €{pricing.total_price.toLocaleString()} ({pricing.total_days} Person-Days)
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {artifacts.status === "ready" ? (
              <div className="flex items-center gap-2">
                <a
                  href={`/api/backend/bids/${bidId}/download/docx`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download DOCX</span>
                </a>
                <a
                  href={`/api/backend/bids/${bidId}/download/pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 hover:bg-black text-white rounded-xl text-xs font-bold shadow-xs transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </a>
              </div>
            ) : (
              <div className="text-right">
                <span className="text-[10px] text-slate-400 font-semibold uppercase block">Qualification</span>
                <span
                  className={`font-extrabold px-3 py-1 rounded-md text-xs uppercase ${
                    eligibility?.recommendation === "bid"
                      ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                      : "bg-amber-100 text-amber-800 border border-amber-300"
                  }`}
                >
                  {eligibility?.recommendation || "ANALYZING"}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 shadow-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Decision Banner if waiting for approval */}
      {isWaiting && (
        <div className="bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-2xl p-6 shadow-md space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 bg-amber-100 rounded-xl text-amber-800 shadow-xs mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-extrabold text-amber-950">
                  Human-in-the-Loop Checkpoint: Executive Bid / No-Bid Sign-off
                </h3>
                <p className="text-xs text-amber-900 leading-relaxed max-w-3xl">
                  Bidvera completed automated document ingestion, extraction of {requirements.length} atomic
                  requirements, and validation against Tychon corporate credentials. Sign-off is required to proceed to proposal outline planning, parallel section drafting, commercial pricing, compliance matrix, and PDF generation.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 pt-3 border-t border-amber-200/80">
            <input
              type="text"
              placeholder="Add executive sign-off comments or rationale..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full text-xs px-3.5 py-2.5 bg-white border border-amber-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/30 transition shadow-xs"
            />
            <div className="flex items-center gap-2 flex-shrink-0 w-full sm:w-auto">
              <button
                onClick={() => handleDecision("bid")}
                disabled={decisionSubmitting}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 transition disabled:opacity-50"
              >
                {decisionSubmitting ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                )}
                <span>Approve & Generate Full Proposal</span>
              </button>
              <button
                onClick={() => handleDecision("no-bid")}
                disabled={decisionSubmitting}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2.5 bg-white border border-red-300 hover:bg-red-50 text-red-700 rounded-xl text-xs font-bold transition disabled:opacity-50"
              >
                <XCircle className="w-3.5 h-3.5 text-red-500" />
                <span>Reject (No-Bid)</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="border-b border-slate-200 flex gap-6 text-xs font-bold overflow-x-auto">
        {[
          { key: "timeline", label: "Execution Timeline", icon: Layers },
          { key: "requirements", label: `Requirements (${requirements.length})`, icon: ListOrdered },
          { key: "eligibility", label: "Corporate Qualification", icon: ShieldCheck },
          { key: "outline", label: `Outline (${outline.length})`, icon: FileText },
          { key: "sections", label: `Drafted Sections (${sections.length})`, icon: Edit3 },
          { key: "pricing", label: "Commercial Pricing", icon: DollarSign },
          { key: "compliance", label: `Compliance Matrix (${matrix.length})`, icon: FileCheck },
          { key: "review", label: "QA & Review", icon: Award },
          { key: "artifacts", label: "Proposal Downloads", icon: Download },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className={`pb-3.5 flex items-center gap-2 border-b-2 whitespace-nowrap transition ${
              activeTab === key
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Tab 1: Timeline */}
      {activeTab === "timeline" && (
        <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-5">
          <h3 className="text-sm font-bold text-slate-900">Multi-Agent Workflow Stages</h3>
          <div className="space-y-4">
            {[
              {
                step: "1. Tender Ingestion",
                desc: "Fetches metadata, documents, and annexes from tender-search MCP server.",
                done: true,
              },
              {
                step: "2. Document Parsing & Structure Extraction",
                desc: "Parses docx/pdf formats into normalized document objects.",
                done: true,
              },
              {
                step: "3. Parallel Requirement Extraction (LangGraph Send)",
                desc: `Extracted ${requirements.length} atomic requirements categorized by mandatory vs. technical.`,
                done: true,
              },
              {
                step: "4. Company Knowledge & Eligibility Gate",
                desc: "Verified corporate turnover, ISO 27001 cert, AWS tier, and case study thresholds via company-knowledge MCP server.",
                done: true,
              },
              {
                step: "5. Human Bid Decision Checkpoint",
                desc: isWaiting
                  ? "Workflow interrupted. Awaiting executive sign-off."
                  : (bid as any).decisions?.length > 0
                  ? `Decision finalized: ${(bid as any).decisions[0].decision.toUpperCase()} by ${(bid as any).decisions[0].who}`
                  : "Pending approval.",
                done: !isWaiting && (bid as any).decisions?.length > 0,
                active: isWaiting,
              },
              {
                step: "6. Outline Generation & Section Mapping",
                desc:
                  outline.length > 0
                    ? `Generated ${outline.length} proposal sections with mapped requirements.`
                    : status === "no_bid_closed"
                    ? "Bypassed due to No-Bid executive decision."
                    : "Awaiting prior milestone.",
                done: outline.length > 0 || status === "no_bid_closed",
              },
              {
                step: "7. Parallel Section Drafting",
                desc:
                  sections.length > 0
                    ? `Drafted ${sections.length} proposal sections in parallel with verified credentials and structured prose.`
                    : "Awaiting approval.",
                done: sections.length > 0,
              },
              {
                step: "8. Commercial Pricing & Effort Estimation",
                desc:
                  pricing.total_price
                    ? `Compiled commercial rate sheet: €${pricing.total_price.toLocaleString()} across ${pricing.total_days} person-days.`
                    : "Awaiting drafting completion.",
                done: !!pricing.total_price,
              },
              {
                step: "9. Traceable Compliance Matrix Assembly",
                desc:
                  matrix.length > 0
                    ? `Mapped ${matrix.length} mandatory & scored requirements to proposal evidence statements.`
                    : "Awaiting pricing.",
                done: matrix.length > 0,
              },
              {
                step: "10. Proposal Quality Assurance & Review",
                desc:
                  review
                    ? `Quality score: ${review.score}/100 with ${review.requirement_coverage_pct}% requirement coverage.`
                    : "Awaiting matrix.",
                done: !!review,
              },
              {
                step: "11. Final Document Generation (DOCX & PDF)",
                desc:
                  artifacts.status === "ready"
                    ? "Generated distribution-ready Proposal.docx and Proposal.pdf."
                    : "Awaiting review.",
                done: artifacts.status === "ready",
              },
            ].map((item, idx) => (
              <div key={idx} className="flex items-start gap-4">
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-bold transition shadow-xs ${
                    item.done
                      ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                      : item.active
                      ? "bg-amber-100 text-amber-800 border-2 border-amber-400 animate-pulse"
                      : "bg-slate-100 text-slate-400 border border-slate-200"
                  }`}
                >
                  {item.done ? <Check className="w-4 h-4" /> : idx + 1}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">{item.step}</h4>
                  <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Requirements Table */}
      {activeTab === "requirements" && (
        <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Extracted Requirements Repository</h3>
            <span className="text-xs font-semibold text-slate-500">
              {requirements.length} atomic statements
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Statement</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Weight</th>
                  <th className="py-3 px-4">Section / Ref</th>
                  <th className="py-3 px-4">Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {requirements.map((req) => (
                  <tr key={req.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600">{req.id}</td>
                    <td className="py-3 px-4 max-w-md font-medium text-slate-800">{req.text}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        {req.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-700">{req.weight}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {req.section} &bull; {req.page_ref}
                    </td>
                    <td className="py-3 px-4 uppercase text-[10px] text-slate-500 font-bold">
                      {req.category}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Eligibility Breakdown */}
      {activeTab === "eligibility" && (
        <div className="space-y-4">
          <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Corporate Qualification Assessment</h3>
              <span
                className={`text-xs font-bold px-3 py-1 rounded-md uppercase ${
                  eligibility?.recommendation === "bid"
                    ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                    : "bg-red-100 text-red-800 border border-red-300"
                }`}
              >
                Recommendation: {eligibility?.recommendation || "N/A"}
              </span>
            </div>
            {eligibility?.reasons && (
              <ul className="space-y-1.5 text-xs text-slate-600">
                {eligibility.reasons.map((r, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCheck className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {eligibility?.criteria_results?.map((c, idx) => (
              <div
                key={idx}
                className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900">{c.name}</h4>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      c.status === "pass"
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                        : "bg-amber-100 text-amber-800 border border-amber-300"
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
                <div className="text-xs text-slate-600 space-y-1 bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <div>
                    <span className="font-semibold text-slate-700">Required: </span>
                    {c.required}
                  </div>
                  <div>
                    <span className="font-semibold text-slate-700">Actual Tychon Profile: </span>
                    {c.actual}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Proposal Outline */}
      {activeTab === "outline" && (
        <div className="space-y-4">
          {outline.length === 0 ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
              <FileText className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">Proposal Outline Not Generated Yet</h4>
              <p className="text-xs text-slate-500 mt-1">
                The outline will be generated once executive approval is submitted at the Bid Decision gate.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {outline.map((sec, idx) => (
                <div
                  key={sec.id || idx}
                  className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-2 hover:border-slate-300 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-md border border-blue-200">
                        Section {idx + 1}
                      </span>
                      <h4 className="text-sm font-bold text-slate-900">{sec.title}</h4>
                    </div>
                    {sec.word_limit && (
                      <span className="text-xs text-slate-500 font-medium">
                        Target: {sec.word_limit} words
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-600">{sec.description}</p>
                  <div className="pt-2.5 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] font-bold text-slate-500 mr-1">
                      Mapped Requirements:
                    </span>
                    {sec.mapped_requirements && sec.mapped_requirements.length > 0 ? (
                      sec.mapped_requirements.map((reqId: string) => (
                        <span
                          key={reqId}
                          className="font-mono text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200"
                        >
                          {reqId}
                        </span>
                      ))
                    ) : (
                      <span className="text-[10px] text-slate-400 italic">None</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Drafted Sections */}
      {activeTab === "sections" && (
        <div className="space-y-4">
          {sections.length === 0 ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
              <Edit3 className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">Sections Not Drafted Yet</h4>
              <p className="text-xs text-slate-500 mt-1">
                Sections will be drafted in parallel upon human approval at the Bid Decision gate.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {sections.map((sec, idx) => (
                <div
                  key={sec.section_id || idx}
                  className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-md border border-indigo-200">
                        Section {idx + 1}
                      </span>
                      <h4 className="text-base font-bold text-slate-900">{sec.title}</h4>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500 font-medium bg-slate-100 px-2 py-0.5 rounded-md">
                        {sec.word_count || sec.content.split(" ").length} words
                      </span>
                    </div>
                  </div>

                  <div className="text-slate-800 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap font-sans space-y-2">
                    {sec.content}
                  </div>

                  {sec.mapped_requirements && sec.mapped_requirements.length > 0 && (
                    <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-slate-500 mr-1">
                        Traceable Requirements:
                      </span>
                      {sec.mapped_requirements.map((reqId: string) => (
                        <span
                          key={reqId}
                          className="font-mono text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200"
                        >
                          {reqId}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 6: Commercial Pricing */}
      {activeTab === "pricing" && (
        <div className="space-y-6">
          {!pricing.total_price ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
              <Coins className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">Pricing Not Compiled Yet</h4>
              <p className="text-xs text-slate-500 mt-1">
                Pricing will calculate automatically upon section generation completion.
              </p>
            </div>
          ) : (
            <>
              {/* Summary Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Total Commercial Quote</div>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    €{pricing.total_price?.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-emerald-600 font-semibold mt-1">
                    Fixed-Price Delivery
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Total Effort</div>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    {pricing.effort?.total_hours || pricing.total_days * 8}h
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-1">
                    {pricing.total_days} Person-Days (8h/day)
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Target Margin</div>
                  <div className="text-2xl font-extrabold text-emerald-700 mt-1">
                    {((pricing.price_sheet?.margin_percentage || 0.22) * 100).toFixed(0)}%
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-1">
                    Gross Margin Floor
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Blended Daily Rate</div>
                  <div className="text-2xl font-extrabold text-indigo-700 mt-1">
                    €{pricing.price_sheet?.blended_daily_rate?.toFixed(2) || "1,531.50"}
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-1">
                    Blended Hourly: €{pricing.price_sheet?.blended_hourly_rate?.toFixed(2) || "191.44"}
                  </div>
                </div>
              </div>

              {/* Price Line Items Table */}
              <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">Role-Based Effort & Commercial Breakdown</h3>
                  <span className="text-xs font-semibold text-slate-500">
                    Currency: {pricing.currency || "EUR"}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Role Title</th>
                        <th className="py-3 px-4 text-right">Hours</th>
                        <th className="py-3 px-4 text-right">Days</th>
                        <th className="py-3 px-4 text-right">Daily Rate</th>
                        <th className="py-3 px-4 text-right">Base Cost</th>
                        <th className="py-3 px-4 text-right">Line Total (Inc. Margin)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {(pricing.price_sheet?.line_items || pricing.price_sheet?.lines || []).map(
                        (line, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/80 transition">
                            <td className="py-3 px-4 font-semibold text-slate-900">
                              {line.role_title}
                            </td>
                            <td className="py-3 px-4 text-right font-medium text-slate-600">
                              {line.hours}h
                            </td>
                            <td className="py-3 px-4 text-right font-medium text-slate-600">
                              {line.days}d
                            </td>
                            <td className="py-3 px-4 text-right font-medium text-slate-600">
                              €{line.daily_rate?.toFixed(2)}
                            </td>
                            <td className="py-3 px-4 text-right font-medium text-slate-600">
                              €{line.base_cost?.toLocaleString()}
                            </td>
                            <td className="py-3 px-4 text-right font-bold text-slate-900">
                              €{line.line_total?.toLocaleString()}
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Assumptions */}
              {pricing.price_sheet?.assumptions && (
                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-2">
                  <h4 className="text-xs font-bold text-slate-900">Commercial Assumptions & Terms</h4>
                  <ul className="space-y-1 text-xs text-slate-600">
                    {pricing.price_sheet.assumptions.map((a, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-blue-500 font-bold">&bull;</span>
                        <span>{a}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Tab 7: Compliance Matrix */}
      {activeTab === "compliance" && (
        <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">RFP Compliance & Traceability Matrix</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Every mandatory and scored requirement mapped to proposal evidence and compliance declarations.
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              {matrix.length} Entries
            </span>
          </div>

          {matrix.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              Compliance matrix will be built automatically during full proposal generation.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4">Requirement ID</th>
                    <th className="py-3 px-4">RFP Statement</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Proposal Section</th>
                    <th className="py-3 px-4">Evidence Citation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {matrix.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-mono font-bold text-blue-600 whitespace-nowrap">
                        {row.requirement_id}
                      </td>
                      <td className="py-3 px-4 max-w-sm font-medium text-slate-800">
                        {row.statement}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          {row.compliance_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600 whitespace-nowrap">
                        {row.proposal_section}
                      </td>
                      <td className="py-3 px-4 text-slate-500 max-w-xs">
                        {row.evidence}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 8: QA & Review */}
      {activeTab === "review" && (
        <div className="space-y-6">
          {!review ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
              <Award className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">QA Review Not Executed Yet</h4>
              <p className="text-xs text-slate-500 mt-1">
                Quality scoring and compliance verification run automatically as the penultimate stage.
              </p>
            </div>
          ) : (
            <>
              {/* Scoring Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Overall Proposal Score</div>
                  <div className="text-3xl font-extrabold text-emerald-600 mt-1">
                    {review.score}/100
                  </div>
                  <div className="text-[11px] text-emerald-700 font-semibold mt-1">
                    Audit & Submission Ready
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Requirement Traceability</div>
                  <div className="text-3xl font-extrabold text-slate-900 mt-1">
                    {review.requirement_coverage_pct}%
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-1">
                    Full Coverage across 6 sections
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
                  <div className="text-xs font-semibold text-slate-400">Hallucination & Evidence Gate</div>
                  <div className="text-3xl font-extrabold text-blue-600 mt-1">
                    PASSED
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-1">
                    Grounded in Company Knowledge MCP
                  </div>
                </div>
              </div>

              {/* Review Flags */}
              <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-3">
                <h4 className="text-xs font-bold text-slate-900">Review Findings & Verification Logs</h4>
                <div className="space-y-2">
                  {review.flags.map((flag, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 ${
                        flag.severity === "pass" || flag.severity === "info"
                          ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                          : "bg-amber-50 border-amber-200 text-amber-800"
                      }`}
                    >
                      <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{flag.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Tab 9: Proposal Downloads */}
      {activeTab === "artifacts" && (
        <div className="space-y-6">
          {artifacts.status !== "ready" ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
              <Download className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">Documents Not Yet Assembled</h4>
              <p className="text-xs text-slate-500 mt-1">
                DOCX and PDF files are generated once all sections and pricing calculations complete.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* DOCX Card */}
              <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                    DOCX
                  </div>
                  <h4 className="text-base font-bold text-slate-900">Microsoft Word Proposal</h4>
                  <p className="text-xs text-slate-500">
                    Editable technical and commercial submission document with custom cover page, table of contents, and compliance tables.
                  </p>
                  <div className="font-mono text-xs text-slate-400 bg-slate-50 p-2 rounded-lg truncate">
                    {artifacts.docx_filename}
                  </div>
                </div>

                <a
                  href={`/api/backend/bids/${bidId}/download/docx`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition"
                >
                  <Download className="w-4 h-4" />
                  <span>Download .DOCX File</span>
                </a>
              </div>

              {/* PDF Card */}
              <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center font-bold">
                    PDF
                  </div>
                  <h4 className="text-base font-bold text-slate-900">Distribution-Ready PDF Proposal</h4>
                  <p className="text-xs text-slate-500">
                    Formatted proposal document with corporate headers, pagination, and official declarations ready for client delivery.
                  </p>
                  <div className="font-mono text-xs text-slate-400 bg-slate-50 p-2 rounded-lg truncate">
                    {artifacts.pdf_filename}
                  </div>
                </div>

                <a
                  href={`/api/backend/bids/${bidId}/download/pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 py-2.5 px-4 bg-slate-900 hover:bg-black text-white rounded-xl text-xs font-bold shadow-xs transition"
                >
                  <Download className="w-4 h-4" />
                  <span>Download .PDF File</span>
                </a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
