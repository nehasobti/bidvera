# Documents MCP Server

The `documents` MCP server generates proposal documents (`.docx`), embeds structured compliance matrices, converts documents to PDF, and provides download endpoints.

## Tools

| Tool | Parameters | Description |
|---|---|---|
| `create_response_doc` | `bid_json: dict`, `template: str` | Generate formal DOCX proposal response document |
| `add_compliance_matrix` | `doc_id: str`, `matrix: list[dict]` | Insert compliance table into an existing document |
| `convert_to_pdf` | `doc_id: str` | Convert proposal DOCX into distribution-ready PDF |
| `get_download_url` | `doc_id: str` | Query file status and download paths |

## Prompts

- `final_checklist`: Pre-flight verification checklist for proposal managers before bid dispatch.

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "bidvera-documents": {
      "command": "python",
      "args": [
        "-m",
        "server",
        "--transport",
        "stdio"
      ],
      "cwd": "path/to/mcp-servers/documents",
      "env": {
        "DOCUMENTS_OUTPUT_DIR": "path/to/output/documents"
      }
    }
  }
}
```

## Running as HTTP / SSE Server

```powershell
python server.py --transport sse --port 8004
```
