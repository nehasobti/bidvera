# Bidvera

> Autonomous Multi-Agent Tender & RFP Response System powered by LangGraph, MCP, and pgvector.

Bidvera is a multi-agent system designed for IT services companies (demonstrated with **Tychon Software**) to discover procurement tenders, extract mandatory requirements, evaluate eligibility, draft evidence-backed technical responses, estimate pricing, and assemble publication-ready documents.

---

## Phase 1 Completed: MCP Servers & Sample Knowledge Base

Four standalone Model Context Protocol (MCP) servers built with the official MCP Python SDK (`FastMCP`) using Dual Transport (stdio for Claude Desktop / MCP Inspector, and Streamable HTTP/SSE with Bearer token authentication):

| Server | Port | Tools | Resources / Prompts |
|---|---|---|---|
| **`tender-search`** | `8001` | `search_tenders`, `get_tender`, `list_documents`, `get_document` | `tender://{tender_id}/summary` |
| **`company-knowledge`** | `8002` | `get_profile`, `search_knowledge`, `find_case_studies`, `list_certifications`, `get_cv` | `company://profile`, prompt `company_voice` |
| **`pricing`** | `8003` | `get_rate_card`, `estimate_effort`, `build_price_sheet` | `pricing://assumptions` |
| **`documents`** | `8004` | `create_response_doc`, `add_compliance_matrix`, `convert_to_pdf`, `get_download_url` | prompt `final_checklist` |

---

## Sample Data Overview

- **Tenders (`sample-data/tenders/`):**
  - `tender-001`: Cloud Migration & Hybrid DevOps Infrastructure (EuroRailways Digital, EU)
  - `tender-002`: Enterprise Healthcare Data Lakehouse & AI Analytics (National Health Consortium, India)
  - `tender-003`: Core Banking Microservices Modernization (Nordic Logistics & FinServices, EU)
- **Tychon Software Knowledge Base (`sample-data/company/`):**
  - Audited corporate profile, €18.5M turnover, 285 engineers
  - Verified ISO 27001, ISO 9001, CMMI Level 3, and AWS Premier Partner accreditations (with expired status handling)
  - 4 detailed delivery case studies with metrics
  - 5 senior staff CVs with certifications and project records
  - Standard multi-currency rate card (`EUR`, `USD`, `INR`) and rule-based effort estimation matrices

---

## How to Test

Run the full test suite (36 unit, integration, and E2E client tests):

```powershell
uv run --python 3.12 --with pytest --with pytest-asyncio --with "mcp<2" --with python-docx --with fpdf2 --with pydantic --with pyyaml --with starlette --with uvicorn pytest -v
```

Run code formatting and type checks:

```powershell
uv run --python 3.12 --with ruff ruff check mcp-servers tests
```

---

## Running MCP Servers Standalone

### Option A: HTTP / SSE Transport
Each server can be launched independently:

```powershell
# In terminal 1:
python mcp-servers/tender-search/server.py --transport sse --port 8001

# In terminal 2:
python mcp-servers/company-knowledge/server.py --transport sse --port 8002

# In terminal 3:
python mcp-servers/pricing/server.py --transport sse --port 8003

# In terminal 4:
python mcp-servers/documents/server.py --transport sse --port 8004
```

Verify health endpoints:
```powershell
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:8002/health
Invoke-RestMethod http://localhost:8003/health
Invoke-RestMethod http://localhost:8004/health
```

### Option B: Claude Desktop Configuration (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "bidvera-tender-search": {
      "command": "python",
      "args": ["-m", "server", "--transport", "stdio"],
      "cwd": "E:\\Workspace\\tychon\\bidvera\\mcp-servers\\tender-search",
      "env": {
        "TENDERS_DATA_DIR": "E:\\Workspace\\tychon\\bidvera\\sample-data\\tenders"
      }
    },
    "bidvera-company-knowledge": {
      "command": "python",
      "args": ["-m", "server", "--transport", "stdio"],
      "cwd": "E:\\Workspace\\tychon\\bidvera\\mcp-servers\\company-knowledge",
      "env": {
        "COMPANY_DATA_DIR": "E:\\Workspace\\tychon\\bidvera\\sample-data\\company"
      }
    },
    "bidvera-pricing": {
      "command": "python",
      "args": ["-m", "server", "--transport", "stdio"],
      "cwd": "E:\\Workspace\\tychon\\bidvera\\mcp-servers\\pricing",
      "env": {
        "COMPANY_DATA_DIR": "E:\\Workspace\\tychon\\bidvera\\sample-data\\company"
      }
    },
    "bidvera-documents": {
      "command": "python",
      "args": ["-m", "server", "--transport", "stdio"],
      "cwd": "E:\\Workspace\\tychon\\bidvera\\mcp-servers\\documents",
      "env": {
        "DOCUMENTS_OUTPUT_DIR": "E:\\Workspace\\tychon\\bidvera\\output\\documents"
      }
    }
  }
}
```
