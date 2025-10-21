#!/bin/sh
# Docker entrypoint script for Shioaji MCP Server
# Supports both stdio and HTTP modes

set -e

# Default mode is stdio
MODE="${MCP_MODE:-stdio}"

echo "Starting Shioaji MCP Server in ${MODE} mode..."

if [ "$MODE" = "http" ]; then
    # HTTP mode
    echo "HTTP API server configuration:"
    echo "  Listen: ${HTTP_LISTEN_HOST:-127.0.0.1}:${HTTP_LISTEN_PORT:-8080}"
    echo "  API Key: ${HTTP_API_KEY:+***configured***}"

    if [ -z "$HTTP_API_KEY" ]; then
        echo "ERROR: HTTP_API_KEY is required for HTTP mode"
        exit 1
    fi

    exec python -m shioaji_mcp.http_server
else
    # stdio mode (default)
    echo "Running in stdio mode (MCP protocol)"
    exec python -m shioaji_mcp.server
fi
