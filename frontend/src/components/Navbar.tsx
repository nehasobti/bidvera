import Link from "next/link";
import { FileText, Inbox, Layers, Search, Sparkles, Shield, ChevronRight, Bot, MessageSquare } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-slate-200/80 shadow-xs transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-500 flex items-center justify-center text-white font-extrabold text-xl shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
              B
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-slate-900 tracking-tight text-lg">Bidvera</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-100/70 text-blue-700 tracking-wide">
                  AI AGENT
                </span>
              </div>
              <span className="text-[11px] text-slate-500 font-medium -mt-0.5">
                Autonomous Tender Intelligence
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation Items */}
        <nav className="flex items-center gap-2">
          <Link
            href="/tenders"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:text-blue-600 hover:bg-slate-100/70 rounded-lg transition"
          >
            <Search className="w-4 h-4 text-slate-500" />
            <span>Tenders</span>
          </Link>

          <Link
            href="/bids"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:text-blue-600 hover:bg-slate-100/70 rounded-lg transition"
          >
            <Layers className="w-4 h-4 text-slate-500" />
            <span>Active Bids</span>
          </Link>

          <Link
            href="/approvals"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100/80 border border-amber-200/80 rounded-lg shadow-xs transition"
          >
            <Inbox className="w-4 h-4 text-amber-600" />
            <span>Approvals Inbox</span>
          </Link>

          <Link
            href="/bids/bid-50b72897"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-lg shadow-sm shadow-blue-500/30 transition"
          >
            <Bot className="w-4 h-4 text-white" />
            <span>AI Copilot</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}

