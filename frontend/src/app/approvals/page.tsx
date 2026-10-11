"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApprovalsInbox, submitBidDecision } from "@/lib/api";
import { Inbox, CheckCircle2, XCircle, AlertTriangle, ArrowRight, ShieldCheck, Clock, UserCheck } from "lucide-react";

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
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Governance & Approvals Inbox</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Human-in-the-loop decision checkpoints: Bid / No-Bid executive sign-offs before generating proposal outlines.
          </p>
        </div>
        <button
          onClick={loadInbox}
          className="self-start sm:self-auto px-3.5 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs transition"
        >
          Refresh Inbox
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 shadow-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {loading && tasks.length === 0 ? (
        <div className="p-16 text-center text-slate-500 bg-white border border-slate-200 rounded-2xl shadow-xs">
          <div className="w-8 h-8 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-700">Polling pending approval gates...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="p-16 text-center bg-white border border-slate-200 rounded-2xl shadow-xs space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-100">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Approvals Inbox is Clear</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            All active bids have either received decision approval or are progressing through automated execution stages.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {tasks.map((task) => {
            const payload = task.interrupt_payload || {};
            const isRecBid = payload.recommendation === "bid";
            return (
              <div
                key={task.bid_id}
                className="bg-white border-2 border-amber-300 rounded-2xl p-6 shadow-md relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500" />

                <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6 pt-2">
                  <div className="space-y-4 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber-900 bg-amber-100/80 px-2.5 py-0.5 rounded-md border border-amber-200">
                        {task.bid_id}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">{task.tender_id}</span>
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                        <Clock className="w-3 h-3 text-amber-600" />
                        Checkpoint: {task.checkpoint}
                      </span>
                    </div>

                    <h2 className="text-lg font-bold text-slate-900 leading-snug">{task.title}</h2>

                    {/* Agent Findings Card */}
                    <div className="bg-slate-50/80 border border-slate-200/80 rounded-xl p-4 space-y-3 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-700 flex items-center gap-1.5">
                          <UserCheck className="w-4 h-4 text-blue-600" />
                          Autonomous Recommendation:
                        </span>
                        <span
                          className={`font-extrabold px-2.5 py-0.5 rounded-md uppercase text-xs shadow-xs ${
                            isRecBid
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                              : "bg-red-100 text-red-800 border border-red-300"
                          }`}
                        >
                          {payload.recommendation || "BID"}
                        </span>
                      </div>

                      {payload.reasons && payload.reasons.length > 0 && (
                        <div className="pt-2.5 border-t border-slate-200">
                          <span className="font-semibold text-slate-700 block mb-1.5">Evidence & Findings:</span>
                          <ul className="space-y-1 text-slate-600">
                            {payload.reasons.map((r: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-emerald-500 font-bold mt-0.5">&bull;</span>
                                <span>{r}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Comment box */}
                    <div>
                      <input
                        type="text"
                        placeholder="Add executive sign-off comments or rationale..."
                        value={comments[task.bid_id] || ""}
                        onChange={(e) =>
                          setComments({ ...comments, [task.bid_id]: e.target.value })
                        }
                        className="w-full text-xs px-3.5 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition"
                      />
                    </div>
                  </div>

                  {/* Actions Column */}
                  <div className="flex flex-col gap-2.5 min-w-[240px] justify-center lg:border-l lg:border-slate-100 lg:pl-6">
                    <button
                      onClick={() => handleDecision(task.bid_id, "bid")}
                      disabled={actionLoading !== null}
                      className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 hover:shadow-lg transition disabled:opacity-50"
                    >
                      {actionLoading === `${task.bid_id}-bid` ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4" />
                      )}
                      <span>Approve (Bid) & Plan Outline</span>
                    </button>

                    <button
                      onClick={() => handleDecision(task.bid_id, "no-bid")}
                      disabled={actionLoading !== null}
                      className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-white border border-red-200 hover:bg-red-50 text-red-700 rounded-xl text-xs font-bold transition disabled:opacity-50"
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
                      className="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 rounded-xl hover:bg-slate-50 transition"
                    >
                      <span>Inspect State & Documents</span>
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
