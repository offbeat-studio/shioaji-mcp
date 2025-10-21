#!/bin/bash
# Test script for Shioaji MCP HTTP API
# This script tests the HTTP API endpoints

set -e

# Configuration
API_KEY="${HTTP_API_KEY:-test_api_key_12345}"
BASE_URL="${SHIOAJI_HTTP_URL:-http://localhost:8080}"

echo "=== Shioaji MCP HTTP API Test ==="
echo "Base URL: $BASE_URL"
echo "API Key: ${API_KEY:0:10}..."
echo ""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expect_auth="$5"

    echo -n "Testing: $name... "

    if [ "$method" = "GET" ]; then
        if [ "$expect_auth" = "true" ]; then
            response=$(curl -s -w "\n%{http_code}" \
                -H "Authorization: Bearer $API_KEY" \
                "$BASE_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
        fi
    else
        response=$(curl -s -w "\n%{http_code}" \
            -X POST \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $status_code)"
        echo "  Response: $(echo $body | head -c 100)..."
    else
        echo -e "${RED}FAIL${NC} (HTTP $status_code)"
        echo "  Response: $body"
    fi
    echo ""
}

# Test 1: Health check (no auth required)
test_endpoint \
    "Health Check" \
    "GET" \
    "/health" \
    "" \
    "false"

# Test 2: List tools (auth required)
test_endpoint \
    "List Tools" \
    "GET" \
    "/api/tools/list" \
    "" \
    "true"

# Test 3: Call tool - get_account_info
test_endpoint \
    "Get Account Info" \
    "POST" \
    "/api/tools/call" \
    '{"tool":"get_account_info","arguments":{}}' \
    "true"

# Test 4: Call tool - search_contracts
test_endpoint \
    "Search Contracts" \
    "POST" \
    "/api/tools/call" \
    '{"tool":"search_contracts","arguments":{"keyword":"台積電"}}' \
    "true"

# Test 5: Test authentication failure
echo -n "Testing: Authentication Failure... "
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer wrong_key" \
    "$BASE_URL/api/tools/list")
status_code=$(echo "$response" | tail -n1)

if [ "$status_code" = "401" ]; then
    echo -e "${GREEN}PASS${NC} (HTTP $status_code - Correctly rejected)"
else
    echo -e "${RED}FAIL${NC} (HTTP $status_code - Should be 401)"
fi
echo ""

# Test 6: Test missing tool parameter
echo -n "Testing: Missing Tool Parameter... "
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"arguments":{}}' \
    "$BASE_URL/api/tools/call")
status_code=$(echo "$response" | tail -n1)

if [ "$status_code" = "400" ]; then
    echo -e "${GREEN}PASS${NC} (HTTP $status_code - Correctly rejected)"
else
    echo -e "${RED}FAIL${NC} (HTTP $status_code - Should be 400)"
fi
echo ""

echo "=== Test Complete ==="
