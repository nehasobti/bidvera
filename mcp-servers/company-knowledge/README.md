# Company Knowledge MCP Server

The `company-knowledge` MCP server manages corporate memory and evidence for Tychon Software, exposing tools to query company profiles, past proposals, case studies, staff credentials, and verified certifications.

## Tools

| Tool | Parameters | Description |
|---|---|---|
| `get_profile` | none | Retrieve official company financials, legal entities, and competencies |
| `search_knowledge` | `query: str`, `doc_types: list[str]`, `top_k: int` | Hybrid search over evidence chunks (case studies, certs, CVs) |
| `find_case_studies` | `tags: list[str]`, `industry: str` | Filter past delivery projects and audited metrics |
| `list_certifications` | none | List ISO, CMMI, and cloud partner accreditations (flags expired) |
| `get_cv` | `role: str`, `skills: list[str]` | Find staff profiles by domain role or technology expertise |

## Resources & Prompts

- `company://profile`: Formatted Markdown summary of company profile.
- Prompt `company_voice`: Voice and style guidelines for writing proposal answers.

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "bidvera-company-knowledge": {
      "command": "python",
      "args": [
        "-m",
        "server",
        "--transport",
        "stdio"
      ],
      "cwd": "path/to/mcp-servers/company-knowledge",
      "env": {
        "COMPANY_DATA_DIR": "path/to/sample-data/company"
      }
    }
  }
}
```

## Running as HTTP / SSE Server

```powershell
python server.py --transport sse --port 8002
```
