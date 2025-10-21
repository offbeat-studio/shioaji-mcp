FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install minimal dependencies and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy all necessary files at once
COPY . .

# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache . && \
    pip uninstall -y uv && \
    apt-get purge -y gcc g++ && \
    apt-get autoremove -y && \
    rm -rf /root/.cache /tmp/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_MODE=stdio

# Create non-root user and set up permissions
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod +x /app/docker-entrypoint.sh

USER appuser

# Support both stdio and HTTP modes via docker-entrypoint.sh
# Set MCP_MODE=http to use HTTP API mode
ENTRYPOINT ["/app/docker-entrypoint.sh"]