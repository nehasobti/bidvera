FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY mcp-servers/company-knowledge/pyproject.toml .
RUN pip install --no-cache-dir .

COPY mcp-servers/company-knowledge/*.py .

EXPOSE 8002

CMD ["python", "server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8002"]
