# Use the official Python lightweight image
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Workdir
WORKDIR /app

# Install deps (use layering for cache)
COPY pyproject.toml uv.lock* ./
# add anything referenced by pyproject metadata:
COPY README.md ./

RUN uv sync --frozen

# Copy the rest of the project
COPY . .

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080

EXPOSE 8080

# Run the FastMCP server
CMD ["uv", "run", "quickchat-ai-mcp"]
