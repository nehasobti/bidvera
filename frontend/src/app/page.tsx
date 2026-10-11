import Link from "next/link";
import {
  Bot,
  Search,
  Layers,
  Inbox,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FileText,
  DollarSign,
  Download,
  Sparkles,
  Cpu,
  FileCheck,
  Coins,
  ExternalLink,
  ChevronRight,
  Award,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="text-center pt-8 pb-12 max-w-4xl mx-auto space-y-6">
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold shadow-2xs">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Multi-Agent LangGraph + FastMCP Architecture Live</span>
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
          Win Enterprise RFPs with{" "}
          <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">
            Autonomous AI Agents
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Bidvera ingests complex multi-document tender packs, extracts mandatory requirements
          in parallel, validates corporate eligibility gates, drafts evidence-grounded responses,
          calculates commercial rate sheets, and generates publication-ready Word & PDF documents.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link
            href="/tenders"
            className="flex items-center gap-2 px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs sm:text-sm font-bold shadow-lg shadow-blue-500/25 transition-all transform hover:-translate-y-0.5"
          >
            <Search className="w-4 h-4" />
            <span>Browse Tender Database</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>

          <Link
            href="/bids"
            className="flex items-center gap-2 px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 rounded-xl text-xs sm:text-sm font-bold shadow-xs transition"
          >
            <Layers className="w-4 h-4 text-slate-500" />
            <span>Active Bid Workspaces</span>
          </Link>

          <Link
            href="/approvals"
            className="flex items-center gap-2 px-6 py-3.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 rounded-xl text-xs sm:text-sm font-bold shadow-xs transition"
          >
            <Inbox className="w-4 h-4 text-amber-600" />
            <span>Approvals Inbox</span>
          </Link>
        </div>

        {/* Live Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-8 text-left">
          {[
            {
              metric: "100%",
              label: "Mandatory Coverage",
              desc: "Automated compliance matrix",
            },
            {
              metric: "0",
              label: "Hallucinated Claims",
              desc: "Strict knowledge citations",
            },
            {
              metric: "4",
              label: "FastMCP Servers",
              desc: "Dual HTTP/SSE & stdio",
            },
            {
              metric: "< 15s",
              label: "Proposal Assembly",
              desc: "DOCX & formatted PDF",
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-xs"
            >
              <div className="text-2xl font-black text-slate-900">{item.metric}</div>
              <div className="text-xs font-bold text-slate-700 mt-0.5">{item.label}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">{item.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* 5-Stage Agent Pipeline Walkthrough */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            How Bidvera Coordinates Multi-Agent Teams
          </h2>
          <p className="text-xs text-slate-500 max-w-xl mx-auto">
            Deterministic LangGraph StateGraph orchestrating specialized agent nodes with persistent checkpoints and human-in-the-loop decisions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            {
              step: "01",
              title: "Ingestion & Parse",
              desc: "Fetches RFP packs and annexes via tender-search MCP. Normalizes Word & PDF documents.",
              icon: Search,
              badge: "FastMCP :8001",
              badgeColor: "bg-blue-50 text-blue-700 border-blue-200",
            },
            {
              step: "02",
              title: "Parallel Extraction",
              desc: "Fans out to section extractors via LangGraph Send, isolating mandatory and scored requirements.",
              icon: Cpu,
              badge: "LangGraph Send",
              badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200",
            },
            {
              step: "03",
              title: "Eligibility Gate",
              desc: "Compares financial turnover, ISO certs, and case studies. Pauses for human bid/no-bid sign-off.",
              icon: ShieldCheck,
              badge: "Human interrupt()",
              badgeColor: "bg-amber-50 text-amber-800 border-amber-200",
            },
            {
              step: "04",
              title: "Drafting & Pricing",
              desc: "Drafts technical sections with verified citations. Pricing analyst computes role-based rates.",
              icon: DollarSign,
              badge: "FastMCP :8003",
              badgeColor: "bg-emerald-50 text-emerald-700 border-emerald-200",
            },
            {
              step: "05",
              title: "Assembly & Matrix",
              desc: "Compiles traceable compliance matrix and renders publication-ready DOCX and PDF documents.",
              icon: FileCheck,
              badge: "FastMCP :8004",
              badgeColor: "bg-purple-50 text-purple-700 border-purple-200",
            },
          ].map((card, idx) => {
            const Icon = card.icon;
            return (
              <div
                key={idx}
                className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3 relative group hover:border-blue-400 transition"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-black text-slate-300">
                      {card.step}
                    </span>
                    <span
                      className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${card.badgeColor}`}
                    >
                      {card.badge}
                    </span>
                  </div>
                  <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center text-slate-700">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{card.title}</h3>
                  <p className="text-[11px] text-slate-500 leading-relaxed">{card.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Featured Sample Tenders Showcase */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Pre-Loaded Procurement Tenders
            </h2>
            <p className="text-xs text-slate-500">
              Audited sample tenders ready for automated ingestion, evaluation, and proposal generation.
            </p>
          </div>
          <Link
            href="/tenders"
            className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 self-start sm:self-auto"
          >
            <span>View All Tenders</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              id: "tender-001",
              title: "Cloud Migration & Hybrid DevOps Infrastructure",
              buyer: "EuroRailways Digital GmbH",
              country: "EU",
              budget: "€2,500,000",
              deadline: "Nov 20, 2026",
              summary:
                "Migration of 380+ legacy virtual workloads to AWS with automated Terraform and ArgoCD GitOps pipelines adhering to 99.95% SLA.",
              tag: "Cloud & DevOps",
            },
            {
              id: "tender-002",
              title: "Enterprise Healthcare Data Lakehouse & AI Analytics",
              buyer: "National Health Consortium",
              country: "India",
              budget: "€1,950,000",
              deadline: "Dec 05, 2026",
              summary:
                "Centralized clinical data lakehouse supporting real-time HL7/FHIR streaming, HIPAA pseudonymization, and predictive AI clinical models.",
              tag: "Data & AI",
            },
            {
              id: "tender-003",
              title: "Core Banking Microservices Modernization",
              buyer: "Nordic Logistics & FinServices AB",
              country: "EU",
              budget: "€3,200,000",
              deadline: "Nov 30, 2026",
              summary:
                "Strangler-fig decomposition of monolithic core transaction processing into Kubernetes microservices with PCI-DSS Level 1 compliance.",
              tag: "FinTech & Banking",
            },
          ].map((t) => (
            <div
              key={t.id}
              className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4 hover:shadow-md transition"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {t.tag}
                  </span>
                  <span className="text-xs font-bold text-slate-900">{t.budget}</span>
                </div>
                <h3 className="text-base font-bold text-slate-900 leading-snug">{t.title}</h3>
                <div className="text-xs text-slate-500 font-medium">
                  {t.buyer} &bull; <span className="font-semibold text-slate-700">{t.country}</span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                  {t.summary}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 font-medium">
                  Deadline: {t.deadline}
                </span>
                <Link
                  href="/tenders"
                  className="px-3.5 py-1.5 bg-slate-900 hover:bg-black text-white rounded-lg text-xs font-bold shadow-xs transition"
                >
                  Start Bid
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FastMCP Ecosystem Architecture Showcase */}
      <section className="bg-slate-900 text-white rounded-3xl p-8 sm:p-10 space-y-6">
        <div className="max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-[11px] font-bold border border-blue-500/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Official Model Context Protocol Ecosystem</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            4 Standalone FastMCP Tool Servers
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Every knowledge source, rate sheet, and document generator runs as an independent MCP service with Bearer token authentication, reusable in Claude Desktop or external clients.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          {[
            {
              name: "tender-search",
              port: ":8001",
              tools: ["search_tenders", "get_tender", "list_documents", "get_document"],
              desc: "Tender catalog discovery & document pack access.",
            },
            {
              name: "company-knowledge",
              port: ":8002",
              tools: ["get_profile", "search_knowledge", "find_case_studies", "list_certifications"],
              desc: "Tychon Software credentials, ISO certs & CVs.",
            },
            {
              name: "pricing",
              port: ":8003",
              tools: ["get_rate_card", "estimate_effort", "build_price_sheet"],
              desc: "Commercial effort matrices and multi-currency rates.",
            },
            {
              name: "documents",
              port: ":8004",
              tools: ["create_response_doc", "add_compliance_matrix", "convert_to_pdf"],
              desc: "Publication-grade DOCX styling and PDF compilation.",
            },
          ].map((mcp, idx) => (
            <div
              key={idx}
              className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-blue-400">{mcp.port}</span>
                <span className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
                  SSE / stdio
                </span>
              </div>
              <h3 className="text-sm font-bold text-white">{mcp.name}</h3>
              <p className="text-[11px] text-slate-400">{mcp.desc}</p>
              <div className="pt-2 border-t border-slate-700/60">
                <span className="text-[10px] text-slate-500 font-semibold block mb-1">
                  Exposed Tools:
                </span>
                <div className="flex flex-wrap gap-1">
                  {mcp.tools.map((t, tIdx) => (
                    <span
                      key={tIdx}
                      className="font-mono text-[9px] bg-slate-900 text-slate-300 px-1.5 py-0.5 rounded border border-slate-800"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div>
          &copy; 2026 <strong className="text-slate-800">Bidvera</strong> &bull; Multi-Agent RFP Automation for Tychon Software.
        </div>
        <div className="flex items-center gap-6">
          <Link href="/tenders" className="hover:text-blue-600 transition">
            Tenders
          </Link>
          <Link href="/bids" className="hover:text-blue-600 transition">
            Active Bids
          </Link>
          <Link href="/approvals" className="hover:text-blue-600 transition">
            Approvals
          </Link>
          <a
            href="http://localhost:8005/docs"
            target="_blank"
            rel="noreferrer"
            className="hover:text-blue-600 transition flex items-center gap-1"
          >
            <span>Agent OpenAPI Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </footer>
    </div>
  );
}
