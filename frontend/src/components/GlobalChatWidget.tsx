"use client";

import { useState, useEffect } from "react";
import { Bot, MessageSquare, X, Send, Sparkles, FileText, ChevronDown } from "lucide-react";
import { executeBidTask, fetchBids } from "@/lib/api";

export function GlobalChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [bids, setBids] = useState<any[]>([]);
  const [selectedBidId, setSelectedBidId] = useState<string>("bid-50b72897");
  const [messages, setMessages] = useState<
    Array<{ sender: "user" | "agent"; text: string; citations?: string[] }>
  >([
    {
      sender: "agent",
      text: "👋 Hi! I am your Autonomous Tender & RFP Chat Agent. Ask me anything about procurement criteria, SLAs, penalty terms, or Tychon Software qualifications.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBids()
      .then((data) => {
        if (data && data.length > 0) {
          setBids(data);
          setSelectedBidId(data[0].bid_id);
        }
      })
      .catch(() => {});
  }, []);

  const handleSend = async (presetText?: string) => {
    const textToSend = presetText || input;
    if (!textToSend.trim() || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { sender: "user", text: textToSend }]);
    setLoading(true);

    try {
      const bidId = selectedBidId || "bid-50b72897";
      const res = await executeBidTask(bidId, "qa", { query: textToSend });
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: res.answer || "No matching clauses found for this query in the tender document.",
          citations: res.citations || [],
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: `Error querying tender agent: ${err.message || "Failed to process request"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Chat Agent Button (Visible on ALL pages) */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Open AI Tender Chat Agent"
          className="relative flex items-center gap-3 px-5 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-full shadow-2xl shadow-blue-500/40 font-bold text-xs tracking-wide transition-all transform hover:scale-105 active:scale-95 cursor-pointer border-2 border-white/30"
        >
          {/* Notification Ping Indicator */}
          <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white"></span>
          </span>

          <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
            {isOpen ? <X className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
          </div>
          <span className="font-extrabold text-sm">Chat with Tender AI</span>
        </button>
      </div>

      {/* Floating Chat Modal / Drawer */}
      {isOpen && (
        <div className="fixed bottom-22 right-6 z-50 w-96 max-w-[calc(100vw-2rem)] h-[540px] bg-white rounded-3xl shadow-2xl border border-slate-200/90 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-slate-900 to-slate-800 text-white flex items-center justify-between border-b border-slate-700/80">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-xs">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="text-xs font-extrabold tracking-tight flex items-center gap-1.5">
                  <span>Tender AI Copilot</span>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-300 font-bold px-1.5 py-0.5 rounded border border-emerald-500/30">
                    ONLINE
                  </span>
                </h4>
                <p className="text-[10px] text-slate-400">Ask about requirements, SLAs & penalty clauses</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-1 rounded-lg transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Active Bid / Tender Selector Bar */}
          {bids.length > 0 && (
            <div className="px-3 py-2 bg-slate-100 border-b border-slate-200 flex items-center justify-between text-[11px]">
              <span className="text-slate-500 font-semibold flex items-center gap-1">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                <span>Context:</span>
              </span>
              <select
                value={selectedBidId}
                onChange={(e) => setSelectedBidId(e.target.value)}
                className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-slate-800 text-[10px] font-bold focus:outline-none max-w-[220px] truncate"
              >
                {bids.map((b) => (
                  <option key={b.bid_id} value={b.bid_id}>
                    {b.title || b.bid_id}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Quick Question Chips */}
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-100 flex items-center gap-1.5 overflow-x-auto text-[10px]">
            <span className="text-slate-400 font-semibold flex-shrink-0">Ask:</span>
            {[
              "What is the availability SLA?",
              "What are the penalty clauses?",
              "What is the turnover threshold?",
            ].map((q, qIdx) => (
              <button
                key={qIdx}
                onClick={() => handleSend(q)}
                className="whitespace-nowrap px-2.5 py-1 rounded-full bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 font-medium transition cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50/40">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-blue-600 text-white font-medium rounded-br-xs"
                      : "bg-white text-slate-800 border border-slate-200 shadow-2xs rounded-bl-xs"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {/* Document Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-100 flex flex-wrap gap-1">
                      <span className="text-[9px] font-bold text-slate-400">Ref:</span>
                      {msg.citations.map((cite, cIdx) => (
                        <span
                          key={cIdx}
                          className="text-[9px] font-bold bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200"
                        >
                          {cite}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-slate-500 text-xs bg-white p-3 rounded-2xl border border-slate-200 w-fit">
                <div className="w-3.5 h-3.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-[11px] font-semibold">Tender AI analyzing documents...</span>
              </div>
            )}
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white border-t border-slate-200 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask anything about this RFP..."
              className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition disabled:opacity-50 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
