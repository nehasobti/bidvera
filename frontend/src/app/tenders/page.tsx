"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, ArrowRight, Building2, MapPin, Calendar, CheckCircle2, AlertTriangle, Play } from "lucide-react";
import { startBid } from "@/lib/api";

const SAMPLE_TENDERS = [
  {
    id: "tender-001",
    title: "Cloud Migration & Hybrid DevOps Infrastructure",
    buyer: "EuroRailways Digital GmbH",
    country: "EU",
    category: "Cloud Migration",
    deadline: "2026-11-20T17:00:00Z",
    budget: "€2,500,000",
    summary:
      "EuroRailways Digital seeks an experienced cloud integration partner to migrate 380+ legacy virtual workloads to AWS and establish automated GitOps DevOps pipelines with 99.95% availability SLA.",
    documentsCount: 2,
    fitScore: 92,
    eligibilityNotice: "Mandatory: €10M+ turnover, ISO 27001, AWS Partner, 8+ yrs experience",
  },
  {
    id: "tender-002",
    title: "Enterprise Healthcare Data Lakehouse & AI Analytics",
    buyer: "National Health Consortium",
    country: "India",
    category: "Data & AI",
    deadline: "2026-12-05T18:00:00Z",
    budget: "€1,950,000",
    summary:
      "Implementation of a centralized, secure clinical data lakehouse, real-time HL7/FHIR streaming ingestion, and predictive AI analytics platform across regional medical hubs.",
    documentsCount: 2,
    fitScore: 84,
    eligibilityNotice: "Mandatory: ₹100 Crore / €11M turnover, CMMI Level 3+, ISO 9001/27001",
  },
  {
    id: "tender-003",
    title: "Core Banking Microservices Modernization",
    buyer: "Nordic Logistics & FinServices AB",
    country: "EU",
    category: "Software Development",
    deadline: "2026-11-30T16:00:00Z",
    budget: "€3,200,000",
    summary:
      "Decomposition of monolithic transaction processing into domain-driven microservices on Kubernetes, API gateway integration, and PCI-DSS compliance.",
    documentsCount: 1,
    fitScore: 78,
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
      t.category.toLowerCase().includes(filter.toLowerCase())
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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Tender Search & Discovery</h1>
          <p className="text-sm text-gray-600 mt-1">
            Browse published RFPs and initialize autonomous multi-agent response workflows.
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search tenders, buyers..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-sm text-red-700">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTenders.map((tender) => (
          <div
            key={tender.id}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                  {tender.category}
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Fit Score: {tender.fitScore}%
                </span>
              </div>

              <h2 className="text-base font-semibold text-gray-900 line-clamp-2 mb-2">
                {tender.title}
              </h2>

              <p className="text-xs text-gray-600 line-clamp-3 mb-4 leading-relaxed">
                {tender.summary}
              </p>

              <div className="space-y-1.5 text-xs text-gray-500 border-t border-gray-100 pt-3 mb-4">
                <div className="flex items-center gap-2">
                  <Building2 className="w-3.5 h-3.5 text-gray-400" />
                  <span className="font-medium text-gray-700">{tender.buyer}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-gray-400" />
                  <span>{tender.country} &bull; Budget: {tender.budget}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5 text-gray-400" />
                  <span>Deadline: {new Date(tender.deadline).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="p-2.5 bg-gray-50 rounded-lg text-[11px] text-gray-600 mb-4 border border-gray-100">
                <span className="font-semibold text-gray-700">Criteria: </span>
                {tender.eligibilityNotice}
              </div>
            </div>

            <button
              onClick={() => handleStartBid(tender.id)}
              disabled={loadingTenderId === tender.id}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingTenderId === tender.id ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Initializing Workflow...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Start Autonomous Bid</span>
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
