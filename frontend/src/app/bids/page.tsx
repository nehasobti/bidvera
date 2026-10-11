"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchBids } from "@/lib/api";
import { Layers, ArrowRight, Clock, AlertCircle, CheckCircle, FileText } from "lucide-react";

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Active Bids</h1>
          <p className="text-sm text-gray-600 mt-1">
            Overview of current bid generation threads, workflow milestones, and approval gates.
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Refresh List
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && bids.length === 0 ? (
        <div className="p-12 text-center text-gray-500 bg-white border border-gray-200 rounded-xl">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-sm">Fetching active bids...</p>
        </div>
      ) : bids.length === 0 ? (
        <div className="p-12 text-center bg-white border border-gray-200 rounded-xl">
          <Layers className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-gray-800">No active bids in progress</h3>
          <p className="text-xs text-gray-500 mt-1 mb-4">
            Start a new bid response workflow from the Tenders page.
          </p>
          <Link
            href="/tenders"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
          >
            Explore Available Tenders
          </Link>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <div className="divide-y divide-gray-200">
            {bids.map((bid) => (
              <div
                key={bid.bid_id}
                className="p-5 hover:bg-gray-50/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {bid.bid_id}
                    </span>
                    <span className="text-xs text-gray-400">&bull;</span>
                    <span className="text-xs text-gray-600 font-medium">{bid.tender_id}</span>
                    {bid.is_waiting_for_approval && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 animate-pulse">
                        <AlertCircle className="w-3 h-3 text-amber-600" />
                        Awaiting Human Decision
                      </span>
                    )}
                    {bid.status === "outline_completed" && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                        <CheckCircle className="w-3 h-3 text-emerald-600" />
                        Outline Ready
                      </span>
                    )}
                    {bid.status === "no_bid_closed" && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-200 text-gray-700">
                        No-Bid Closed
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-gray-900">{bid.title}</h3>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>Buyer: <strong className="text-gray-700">{bid.buyer || "N/A"}</strong></span>
                    <span>Requirements: <strong className="text-gray-700">{bid.requirements_count}</strong></span>
                    <span>
                      Recommendation:{" "}
                      <strong
                        className={
                          bid.eligibility_recommendation === "bid"
                            ? "text-emerald-600"
                            : bid.eligibility_recommendation === "no-bid"
                            ? "text-red-600"
                            : "text-amber-600"
                        }
                      >
                        {bid.eligibility_recommendation.toUpperCase()}
                      </strong>
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    href={`/bids/${bid.bid_id}`}
                    className="flex items-center gap-1.5 px-4 py-2 bg-gray-900 hover:bg-black text-white rounded-lg text-xs font-medium transition"
                  >
                    <span>Open Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
