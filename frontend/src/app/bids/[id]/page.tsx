"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { fetchBid, submitBidDecision } from "@/lib/api";
import { BidRecord, Requirement, OutlineSection } from "@/types";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Layers,
  ShieldCheck,
  ChevronRight,
  ListOrdered,
  ArrowLeft,
  Check,
  RotateCw,
} from "lucide-react";

export default function BidWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const bidId = resolvedParams.id;

  const [bid, setBid] = useState<BidRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"timeline" | "requirements" | "eligibility" | "outline">(
    "timeline"
  );
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
      <div className="p-12 text-center text-gray-500 bg-white border border-gray-200 rounded-xl">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm font-medium">Loading bid workspace...</p>
      </div>
    );
  }

  if (!bid) {
    return (
      <div className="p-8 text-center bg-white border border-gray-200 rounded-xl">
        <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
        <p className="text-sm text-gray-700">Bid not found or error loading state.</p>
        <Link href="/bids" className="mt-4 inline-block text-xs text-blue-600 hover:underline">
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

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Header */}
      <div className="space-y-2">
        <Link
          href="/bids"
          className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-900 transition mb-1"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All Bids</span>
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-gray-600 bg-gray-100 px-2.5 py-0.5 rounded">
                {bidId}
              </span>
              <span className="text-xs text-gray-400">&bull;</span>
              <span className="text-xs font-semibold text-blue-600 uppercase">
                {bid.bid?.category || "TENDER"}
              </span>
              {isWaiting && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 animate-pulse">
                  <Clock className="w-3.5 h-3.5 text-amber-600" />
                  Awaiting Decision Checkpoint
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              {bid.bid?.title || bid.tender_id}
            </h1>
            <p className="text-xs text-gray-500">
              Buyer: <strong className="text-gray-700">{bid.bid?.buyer || "N/A"}</strong> &bull; Deadline:{" "}
              {bid.bid?.deadline ? new Date(bid.bid.deadline).toLocaleDateString() : "N/A"}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadBidData}
              className="p-2 text-gray-500 hover:text-gray-800 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 transition"
              title="Refresh"
            >
              <RotateCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Decision Banner if waiting for approval */}
      {isWaiting && (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-100 rounded-lg text-amber-700 mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-amber-900">
                  Human-in-the-Loop Gate: Bid / No-Bid Decision Required
                </h3>
                <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">
                  The automated agents have ingested the RFP, parsed all annexes, extracted {requirements.length}{" "}
                  requirements, and completed corporate eligibility checks. Executive sign-off is required to proceed.
                </p>
              </div>
            </div>

            <div className="text-right flex-shrink-0">
              <span className="text-[10px] text-gray-500 uppercase font-semibold block">Agent Recommendation</span>
              <span className="inline-block mt-0.5 px-2.5 py-0.5 text-xs font-bold rounded bg-emerald-100 text-emerald-800 border border-emerald-300 uppercase">
                {eligibility?.recommendation || "BID"}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2 border-t border-amber-200">
            <input
              type="text"
              placeholder="Add commentary or rationale (optional)..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full text-xs px-3 py-2 bg-white border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
            <div className="flex items-center gap-2 flex-shrink-0 w-full sm:w-auto">
              <button
                onClick={() => handleDecision("bid")}
                disabled={decisionSubmitting}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
              >
                {decisionSubmitting ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                )}
                <span>Approve & Build Outline</span>
              </button>
              <button
                onClick={() => handleDecision("no-bid")}
                disabled={decisionSubmitting}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2 bg-white border border-red-300 hover:bg-red-50 text-red-700 rounded-lg text-xs font-semibold transition disabled:opacity-50"
              >
                <XCircle className="w-3.5 h-3.5 text-red-500" />
                <span>Reject (No-Bid)</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 flex gap-6">
        <button
          onClick={() => setActiveTab("timeline")}
          className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "timeline"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-800"
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Workflow Execution</span>
        </button>
        <button
          onClick={() => setActiveTab("requirements")}
          className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "requirements"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-800"
          }`}
        >
          <ListOrdered className="w-4 h-4" />
          <span>Requirements ({requirements.length})</span>
        </button>
        <button
          onClick={() => setActiveTab("eligibility")}
          className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "eligibility"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-800"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Eligibility Breakdown</span>
        </button>
        <button
          onClick={() => setActiveTab("outline")}
          className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "outline"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-800"
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Proposal Outline ({outline.length})</span>
        </button>
      </div>

      {/* Tab 1: Timeline */}
      {activeTab === "timeline" && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Autonomous Multi-Agent Lifecycle</h3>
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
                step: "3. Parallel Requirement Fan-Out (LangGraph Send)",
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
                  ? "Workflow interrupted. Waiting for human approval via resume."
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
            ].map((item, idx) => (
              <div key={idx} className="flex items-start gap-4">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                    item.done
                      ? "bg-emerald-100 text-emerald-700"
                      : item.active
                      ? "bg-amber-100 text-amber-700 animate-pulse border-2 border-amber-400"
                      : "bg-gray-100 text-gray-400"
                  }`}
                >
                  {item.done ? <Check className="w-4 h-4" /> : idx + 1}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-gray-900">{item.step}</h4>
                  <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Requirements Table */}
      {activeTab === "requirements" && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-sm font-bold text-gray-900">Extracted Requirements</h3>
            <span className="text-xs font-semibold text-gray-500">
              Total: {requirements.length} atomic statements
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-700 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-2.5 px-4">ID</th>
                  <th className="py-2.5 px-4">Statement</th>
                  <th className="py-2.5 px-4">Type</th>
                  <th className="py-2.5 px-4">Weight</th>
                  <th className="py-2.5 px-4">Section / Ref</th>
                  <th className="py-2.5 px-4">Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {requirements.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50/60">
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-600">{req.id}</td>
                    <td className="py-2.5 px-4 max-w-md font-medium">{req.text}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-700">
                        {req.type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-gray-600">{req.weight}</td>
                    <td className="py-2.5 px-4 text-gray-500">
                      {req.section} &bull; {req.page_ref}
                    </td>
                    <td className="py-2.5 px-4 uppercase text-[10px] text-gray-400 font-bold">
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
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-gray-900">Corporate Assessment</h3>
              <span
                className={`text-xs font-bold px-3 py-1 rounded uppercase ${
                  eligibility?.recommendation === "bid"
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                Recommendation: {eligibility?.recommendation || "N/A"}
              </span>
            </div>
            {eligibility?.reasons && (
              <ul className="list-disc list-inside space-y-1 text-xs text-gray-600">
                {eligibility.reasons.map((r, idx) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {eligibility?.criteria_results?.map((c, idx) => (
              <div
                key={idx}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-2"
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-gray-900">{c.name}</h4>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      c.status === "pass"
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
                <div className="text-[11px] text-gray-600 space-y-1">
                  <div>
                    <span className="font-semibold text-gray-700">Required: </span>
                    {c.required}
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Actual Tychon Profile: </span>
                    {c.actual}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Outline Structure */}
      {activeTab === "outline" && (
        <div className="space-y-4">
          {outline.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
              <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <h4 className="text-sm font-semibold text-gray-800">Proposal Outline Not Generated Yet</h4>
              <p className="text-xs text-gray-500 mt-1">
                The outline will be generated once executive approval is granted at the Bid Decision gate.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {outline.map((sec, idx) => (
                <div
                  key={sec.id || idx}
                  className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                        Section {idx + 1}
                      </span>
                      <h4 className="text-sm font-bold text-gray-900">{sec.title}</h4>
                    </div>
                    {sec.target_pages && (
                      <span className="text-xs text-gray-500 font-medium">
                        Target: {sec.target_pages} pages
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600">{sec.description}</p>
                  <div className="pt-2 border-t border-gray-100 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] font-semibold text-gray-500 mr-1">
                      Mapped Requirements:
                    </span>
                    {sec.mapped_requirements && sec.mapped_requirements.length > 0 ? (
                      sec.mapped_requirements.map((reqId: string) => (
                        <span
                          key={reqId}
                          className="font-mono text-[10px] font-bold text-gray-700 bg-gray-100 px-1.5 py-0.5 rounded border border-gray-200"
                        >
                          {reqId}
                        </span>
                      ))
                    ) : (
                      <span className="text-[10px] text-gray-400 italic">None</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
