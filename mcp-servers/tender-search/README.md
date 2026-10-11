# Tender Search MCP Server

The `tender-search` MCP server exposes tools to query procurement tenders, inspect detailed tender specifications, retrieve attached document catalogs, and extract RFP document content with section and table recognition.

## Tools

| Tool | Parameters | Description |
|---|---|---|
| `search_tenders` | `query: str`, `country: str`, `category: str`, `deadline_after: str` | Search and filter tenders matching criteria |
| `get_tender` | `tender_id: str` | Fetch complete tender metadata and eligibility criteria |
| `list_documents` | `tender_id: str` | List RFP documents, annexes, and technical specs |
| `get_document` | `tender_id: str`, `doc_id: str` | Read and parse document text, sections, and tables |

## Resources

- `tender://{tender_id}/summary`: Formatted Markdown summary of the tender's scope and requirements.

## Claude Desktop Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bidvera-tender-search": {
      "command": "python",
      "args": [
        "-m",
        "server",
        "--transport",
        "stdio"
      ],
      "cwd": "path/to/mcp-servers/tender-search",
      "env": {
        "TENDERS_DATA_DIR": "path/to/sample-data/tenders"
      }
    }
  }
}
```

## Running as HTTP / SSE Server

```powershell
python server.py --transport sse --port 8001
```

Health check:
```powershell
curl http://localhost:8001/health
```
