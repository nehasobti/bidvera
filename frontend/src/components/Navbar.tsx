import Link from "next/link";
import { FileText, Inbox, Layers, CheckCircle2, Search } from "lucide-react";

export function Navbar() {
  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
              B
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-gray-900 tracking-tight text-lg">Bidvera</span>
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold -mt-1">
                Autonomous Tender Agent
              </span>
            </div>
          </Link>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/tenders"
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition"
          >
            <Search className="w-4 h-4 text-gray-500" />
            Tenders
          </Link>
          <Link
            href="/bids"
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition"
          >
            <Layers className="w-4 h-4 text-gray-500" />
            Active Bids
          </Link>
          <Link
            href="/approvals"
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-md transition"
          >
            <Inbox className="w-4 h-4 text-amber-600" />
            Approvals Inbox
          </Link>
        </nav>
      </div>
    </header>
  );
}
