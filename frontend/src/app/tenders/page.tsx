"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  ArrowRight,
  Building2,
  MapPin,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Play,
  Sparkles,
  FileText,
  ShieldCheck,
  TrendingUp,
  Layers,
} from "lucide-react";
import { startBid } from "@/lib/api";
import { formatDate } from "@/lib/date";

const SAMPLE_TENDERS = [
  {
    id: "tender-001",
    title: "Cloud Migration & Hybrid DevOps Infrastructure",
    buyer: "EuroRailways Digital GmbH",
    country: "European Union",
    category: "Cloud & Infrastructure",
    deadline: "2026-11-20T17:00:00Z",
    budget: "€2,500,000",
    summary:
      "EuroRailways Digital seeks an experienced cloud integration partner to migrate 380+ legacy virtual workloads to AWS and establish automated GitOps DevOps pipelines with 99.95% availability SLA.",
    documentsCount: 2,
    fitScore: 94,
    tags: ["AWS Premier", "DevOps", "ISO 27001", "Migration"],
    eligibilityNotice: "Mandatory: €10M+ turnover, ISO 27001, AWS Partner, 8+ yrs experience",
  },
  {
    id: "tender-002",
    title: "Enterprise Healthcare Data Lakehouse & AI Analytics",
    buyer: "National Health Consortium",
    country: "India",
    category: "Data Engineering & AI",
    deadline: "2026-12-05T18:00:00Z",
    budget: "€1,950,000",
    summary:
      "Implementation of a centralized, secure clinical data lakehouse, real-time HL7/FHIR streaming ingestion, and predictive AI analytics platform across regional medical hubs.",
    documentsCount: 2,
    fitScore: 88,
    tags: ["Healthcare", "Data Lakehouse", "HL7/FHIR", "CMMI-3"],
    eligibilityNotice: "Mandatory: ₹100 Crore / €11M turnover, CMMI Level 3+, ISO 9001/27001",
  },
  {
    id: "tender-003",
    title: "Core Banking Microservices Modernization",
    buyer: "Nordic Logistics & FinServices AB",
    country: "Nordics",
    category: "Fintech & Microservices",
    deadline: "2026-11-30T16:00:00Z",
    budget: "€3,200,000",
    summary:
      "Decomposition of monolithic transaction processing into domain-driven microservices on Kubernetes, API gateway integration, and PCI-DSS compliance.",
    documentsCount: 1,
    fitScore: 82,
    tags: ["Core Banking", "Kubernetes", "Fintech", "PCI-DSS"],
    eligibilityNotice: "Mandatory: €12M turnover, Financial services ref, ISO 27001",
  },
];

export default function TendersPage() {
  const router = useRouter();
  const [filter, setFilter] = useState("");
  const [loadingTenderId, setLoadingTenderId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const filteredTenders = SAMPLE_TENDERS.filter(
    (t) =>
      t.title.toLowerCase().includes(filter.toLowerCase()) ||
      t.buyer.toLowerCase().includes(filter.toLowerCase()) ||
      t.category.toLowerCase().includes(filter.toLowerCase()) ||
      t.tags.some((tag) => tag.toLowerCase().includes(filter.toLowerCase()))
  );

  const handleStartBid = async (tenderId: string) => {
    try {
      setLoadingTenderId(tenderId);
      setErrorMessage(null);
      const res = await startBid(tenderId);
      if (res && res.bid_id) {
        router.push(`/bids/${res.bid_id}`);
      } else {
        router.push("/bids");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to start bid. Ensure backend is running on port 8005.");
    } finally {
      setLoadingTenderId(null);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Hero Banner Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-blue-950 p-8 sm:p-10 text-white shadow-xl">
        <div className="absolute -right-16 -top-16 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-32 -bottom-20 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-semibold backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            <span>Autonomous Bid Orchestration Platform</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Discover RFPs, Check Eligibility, & Orchestrate Win Proposals.
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
            Bidvera reads full RFP specifications, extracts structured compliance requirements, verifies corporate credentials against Tychon repositories, and generates winning responses.
          </p>
        </div>

        {/* Quick Stats Banner */}
        <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-white/10 text-xs">
          <div>
            <div className="text-slate-400">Total Active RFPs</div>
            <div className="text-xl font-bold text-white mt-0.5">3 Available</div>
          </div>
          <div>
            <div className="text-slate-400">Target Value</div>
            <div className="text-xl font-bold text-white mt-0.5">€7,650,000</div>
          </div>
          <div>
            <div className="text-slate-400">AI Qualification</div>
            <div className="text-xl font-bold text-emerald-400 mt-0.5">LangGraph Agents</div>
          </div>
          <div>
            <div className="text-slate-400">Human Governance</div>
            <div className="text-xl font-bold text-amber-400 mt-0.5">Interactive Gate</div>
          </div>
        </div>
      </div>

      {/* Search & Filter Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Available Tender Opportunities</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Select a published procurement package to launch the agent workflow.
          </p>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search tenders, buyers, skills..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs sm:text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
          />
        </div>
      </div>

      {/* Error message */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-xs text-red-700 shadow-xs">
          <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Tender Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTenders.map((tender) => (
          <div
            key={tender.id}
            className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-200 flex flex-col justify-between group"
          >
            <div>
              {/* Top Tag Row */}
              <div className="flex items-center justify-between gap-2 mb-4">
                <span className="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                  {tender.category}
                </span>

                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-bold shadow-xs">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Fit {tender.fitScore}%</span>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition leading-snug mb-2">
                {tender.title}
              </h3>

              {/* Summary */}
              <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed font-normal">
                {tender.summary}
              </p>

              {/* Metadata Details */}
              <div className="space-y-2 text-xs text-slate-600 bg-slate-50/70 rounded-xl p-3.5 border border-slate-100 mb-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-medium">Buyer:</span>
                  <span className="font-semibold text-slate-800 text-right truncate max-w-[180px]">
                    {tender.buyer}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-medium">Budget:</span>
                  <span className="font-bold text-slate-900">{tender.budget}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-medium">Deadline:</span>
                  <span className="font-medium text-slate-700">{formatDate(tender.deadline)}</span>
                </div>
              </div>

              {/* Skill Tags */}
              <div className="flex flex-wrap gap-1.5 mb-5">
                {tender.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Launch Action Button */}
            <button
              onClick={() => handleStartBid(tender.id)}
              disabled={loadingTenderId === tender.id}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group-hover:translate-y-[-1px]"
            >
              {loadingTenderId === tender.id ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Launching Agent Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Start Autonomous Bid</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-0.5 opacity-80" />
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
