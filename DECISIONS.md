# Architectural & Implementation Decisions (DECISIONS.md)

This log records design decisions, trade-offs, and library choices made during the implementation of Bidvera, adhering to the technical specification.

---

## 1. MCP Python SDK Version Pinning (`mcp>=1.3.0,<2.0.0`)
- **Context:** The official MCP Python SDK introduced breaking changes in 2.x (renaming `FastMCP` to `MCPServer`, removing `RequestContext` from `mcp.shared.context`). `langchain-mcp-adapters` requires `from mcp.shared.context import RequestContext` and depends on the 1.x FastMCP architecture.
- **Decision:** Pin `mcp>=1.3.0,<2.0.0` across all MCP servers and agent clients. This guarantees full compatibility with FastMCP, Streamable HTTP/SSE, and LangChain's `MultiServerMCPClient`.

---

## 2. MCP Transport Protocols (Dual-Mode: Stdio and Streamable HTTP)
- **Context:** The spec requires MCP servers to be runnable as standalone packages reusable with Claude Desktop (`stdio`) and inside Docker Compose as Streamable HTTP services with Bearer token auth.
- **Decision:** Each MCP server CLI supports dual transport via flags/environment variables:
  - Default / `--transport sse` or `--transport http`: Runs a Starlette/FastMCP ASGI server with Bearer token authentication middleware and a public `/health` endpoint.
  - `--transport stdio`: Runs standard I/O transport, enabling direct integration into Claude Desktop or MCP Inspector without extra networking overhead.

---

## 3. Storage and Hybrid Retrieval Fallback in `company-knowledge`
- **Context:** The system uses PostgreSQL with pgvector for production knowledge indexing. However, developers and CI tests frequently run standalone MCP servers or test with Claude Desktop without a live PostgreSQL instance.
- **Decision:** The `company-knowledge` store implements an abstraction layer:
  - When `DATABASE_URL` is set and reachable, it connects to PostgreSQL + pgvector and issues vector + tsvector full-text queries.
  - When running offline or in unit tests, it falls back to an in-memory hybrid store (BM25 + TF-IDF cosine similarity) loaded directly from `sample-data/company/`.
  - Expired certifications and stale CVs are flagged and excluded from evidence ranking by default.

---

## 4. Document Parsing & Ingestion Strategy
- **Context:** Docling provides advanced document extraction (tables, layout, page numbers). However, Docling pulls heavy C++ / OCR dependencies that may not always be available in lightweight environments.
- **Decision:** A modular document ingestion engine is used:
  - If `docling` is installed, it is utilized for deep document conversion.
  - A built-in fallback parser extracts text, tables, and sections from `.docx` (via `python-docx`), `.json`, and `.txt` with exact section headings and metadata, guaranteeing reliable execution in all environments.

---

## 5. Document Generation & PDF Conversion in `documents`
- **Context:** Response documents are generated in `.docx` and converted to `.pdf` via headless LibreOffice. LibreOffice may not be pre-installed on local developer Windows machines without Docker.
- **Decision:** The `documents` MCP server generates Word files using `python-docx` with styled tables, callouts, and compliance matrices. For PDF conversion, it attempts LibreOffice headless CLI; if unavailable, it generates a clean formatted PDF fallback using Python layout primitives, ensuring `convert_to_pdf` consistently returns a valid, downloadable PDF file.

---

## 6. Monorepo Organization
- **Context:** The specification lists:
  - `agent/`
  - `mcp-servers/`
  - `sample-data/`
  - `frontend/`
  - `evals/`
- **Decision:** The workspace root houses `mcp-servers/`, `sample-data/`, `agent/`, and `evals/`, with `docker-compose.yml` orchestrating all services together.
