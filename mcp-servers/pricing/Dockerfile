FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY mcp-servers/pricing/pyproject.toml .
RUN pip install --no-cache-dir .

COPY mcp-servers/pricing/*.py .

EXPOSE 8003

CMD ["python", "server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8003"]
