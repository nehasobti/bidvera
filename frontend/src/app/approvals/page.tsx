"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApprovalsInbox, submitBidDecision } from "@/lib/api";
import { Inbox, CheckCircle2, XCircle, AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";

export default function ApprovalsPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [comments, setComments] = useState<{ [key: string]: string }>({});

  const loadInbox = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchApprovalsInbox();
      setTasks(data);
    } catch (err: any) {
      setError(err.message || "Failed to load approvals inbox");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInbox();
    const interval = setInterval(loadInbox, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleDecision = async (bidId: string, decision: "bid" | "no-bid") => {
    try {
      setActionLoading(`${bidId}-${decision}`);
      setError(null);
      await submitBidDecision(bidId, decision, comments[bidId] || "", "Bid Director");
      await loadInbox();
    } catch (err: any) {
      setError(err.message || "Failed to submit decision");
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Approvals & Governance Inbox</h1>
          <p className="text-sm text-gray-600 mt-1">
            Human-in-the-loop checkpoints: Bid/No-Bid decision gates before generating proposals.
          </p>
        </div>
        <button
          onClick={loadInbox}
          className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Refresh Inbox
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {loading && tasks.length === 0 ? (
        <div className="p-12 text-center text-gray-500 bg-white border border-gray-200 rounded-xl">
          <div className="w-6 h-6 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-sm">Checking approval tasks...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="p-12 text-center bg-white border border-gray-200 rounded-xl">
          <Inbox className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-gray-800">Inbox is Clear</h3>
          <p className="text-xs text-gray-500 mt-1">
            There are no bids currently waiting for human bid/no-bid approval.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => {
            const payload = task.interrupt_payload || {};
            const isRecBid = payload.recommendation === "bid";
            return (
              <div
                key={task.bid_id}
                className="bg-white border border-amber-200 rounded-xl p-6 shadow-sm relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 bottom-0 w-1.5 bg-amber-500" />

                <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                        {task.bid_id}
                      </span>
                      <span className="text-xs font-medium text-gray-500">{task.tender_id}</span>
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        Gate: {task.checkpoint}
                      </span>
                    </div>

                    <h2 className="text-lg font-bold text-gray-900">{task.title}</h2>

                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-gray-700">Agent Recommendation:</span>
                        <span
                          className={`font-bold px-2 py-0.5 rounded uppercase text-[11px] ${
                            isRecBid
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {payload.recommendation || "BID"}
                        </span>
                      </div>

                      {payload.reasons && payload.reasons.length > 0 && (
                        <div className="pt-2 border-t border-gray-200">
                          <span className="font-medium text-gray-600 block mb-1">Key Findings:</span>
                          <ul className="list-disc list-inside space-y-0.5 text-gray-600">
                            {payload.reasons.map((r: string, idx: number) => (
                              <li key={idx}>{r}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    <div>
                      <input
                        type="text"
                        placeholder="Add executive comments or justification (optional)..."
                        value={comments[task.bid_id] || ""}
                        onChange={(e) =>
                          setComments({ ...comments, [task.bid_id]: e.target.value })
                        }
                        className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                      />
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row lg:flex-col gap-2 min-w-[220px] justify-center">
                    <button
                      onClick={() => handleDecision(task.bid_id, "bid")}
                      disabled={actionLoading !== null}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
                    >
                      {actionLoading === `${task.bid_id}-bid` ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4" />
                      )}
                      <span>Approve & Generate Outline</span>
                    </button>

                    <button
                      onClick={() => handleDecision(task.bid_id, "no-bid")}
                      disabled={actionLoading !== null}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-red-300 hover:bg-red-50 text-red-700 rounded-lg text-xs font-semibold transition disabled:opacity-50"
                    >
                      {actionLoading === `${task.bid_id}-no-bid` ? (
                        <div className="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span>Reject (No-Bid)</span>
                    </button>

                    <Link
                      href={`/bids/${task.bid_id}`}
                      className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition mt-1"
                    >
                      <span>Inspect Details</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
