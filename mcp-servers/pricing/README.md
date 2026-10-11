# Pricing MCP Server

The `pricing` MCP server provides commercial rate-card lookups, automated rule-based effort estimation from scope items, and commercial price sheet generation with margin calculations.

## Tools

| Tool | Parameters | Description |
|---|---|---|
| `get_rate_card` | `currency: str = "EUR"` | Retrieve daily and hourly billing rates by seniority in EUR, USD, or INR |
| `estimate_effort` | `scope_items: list[dict]` | Compute hours by role using category baselines and complexity multipliers |
| `build_price_sheet` | `lines: list[dict]`, `currency: str`, `margin: float` | Generate pricing sheet with base cost, margin, total, and blended rate |

## Resources

- `pricing://assumptions`: Markdown summary of standard commercial rules and contractual assumptions.

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "bidvera-pricing": {
      "command": "python",
      "args": [
        "-m",
        "server",
        "--transport",
        "stdio"
      ],
      "cwd": "path/to/mcp-servers/pricing",
      "env": {
        "COMPANY_DATA_DIR": "path/to/sample-data/company"
      }
    }
  }
}
```

## Running as HTTP / SSE Server

```powershell
python server.py --transport sse --port 8003
```
