FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install minimal dependencies and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy and install dependencies
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache . && \
    pip uninstall -y uv && \
    apt-get purge -y gcc g++ && \
    apt-get autoremove -y && \
    rm -rf /root/.cache /tmp/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd -r -s /bin/false appuser
USER appuser

# MCP stdio mode
ENTRYPOINT ["python", "-m", "shioaji_mcp.server"]