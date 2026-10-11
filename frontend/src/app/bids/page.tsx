"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchBids } from "@/lib/api";
import { Layers, ArrowRight, Clock, AlertCircle, CheckCircle, FileText, Sparkles, Building2 } from "lucide-react";

export default function BidsPage() {
  const [bids, setBids] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBids();
      setBids(data);
    } catch (err: any) {
      setError(err.message || "Failed to load active bids");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Active Bid Threads</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time status of LangGraph agent threads, extracted requirements, and human checkpoints.
          </p>
        </div>
        <button
          onClick={loadData}
          className="self-start sm:self-auto px-3.5 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs transition"
        >
          Refresh Threads
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 shadow-xs">
          {error}
        </div>
      )}

      {loading && bids.length === 0 ? (
        <div className="p-16 text-center text-slate-500 bg-white border border-slate-200 rounded-2xl shadow-xs">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-700">Connecting to Bidvera agent threads...</p>
        </div>
      ) : bids.length === 0 ? (
        <div className="p-16 text-center bg-white border border-slate-200 rounded-2xl shadow-xs space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
            <Layers className="w-7 h-7" />
          </div>
          <div className="max-w-sm mx-auto">
            <h3 className="text-base font-bold text-slate-900">No Active Bid Threads</h3>
            <p className="text-xs text-slate-500 mt-1">
              Select an RFP from the tender discovery catalog to initiate automated parsing and qualification.
            </p>
          </div>
          <Link
            href="/tenders"
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-500/20 hover:shadow-lg transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Browse Tender Catalog</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {bids.map((bid) => (
            <div
              key={bid.bid_id}
              className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition-all duration-200 flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[11px] font-bold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md border border-slate-200">
                    {bid.bid_id}
                  </span>
                  <span className="text-[11px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">
                    {bid.tender_id}
                  </span>

                  {bid.is_waiting_for_approval && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300 animate-pulse">
                      <Clock className="w-3.5 h-3.5 text-amber-600" />
                      Pending Executive Decision
                    </span>
                  )}
                  {bid.status === "outline_completed" && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      Outline Ready
                    </span>
                  )}
                  {bid.status === "no_bid_closed" && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                      No-Bid Closed
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-slate-900">{bid.title}</h3>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                  <span className="flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <strong className="text-slate-700">{bid.buyer || "N/A"}</strong>
                  </span>
                  <span>&bull;</span>
                  <span>
                    Requirements: <strong className="text-slate-700 font-bold">{bid.requirements_count}</strong>
                  </span>
                  <span>&bull;</span>
                  <span>
                    Recommendation:{" "}
                    <span
                      className={`font-bold px-1.5 py-0.5 rounded text-[11px] uppercase ${
                        bid.eligibility_recommendation === "bid"
                          ? "bg-emerald-100 text-emerald-800"
                          : bid.eligibility_recommendation === "no-bid"
                          ? "bg-red-100 text-red-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {bid.eligibility_recommendation}
                    </span>
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href={`/bids/${bid.bid_id}`}
                  className="w-full md:w-auto flex items-center justify-center gap-1.5 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-xs hover:shadow-md transition"
                >
                  <span>Open Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
