#!/bin/bash
# Test Docker setup for Shioaji MCP server
# This script helps verify that Docker is properly configured for running the Shioaji MCP server

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Shioaji MCP Docker Setup Test${NC}"
echo "This script will test your Docker setup for running the Shioaji MCP server."
echo

# Check if Docker is installed
echo -n "Checking if Docker is installed... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
    DOCKER_VERSION=$(docker --version)
    echo "Docker version: $DOCKER_VERSION"
else
    echo -e "${RED}FAILED${NC}"
    echo "Docker is not installed or not in PATH. Please install Docker first."
    exit 1
fi

echo

# Check if Docker daemon is running
echo -n "Checking if Docker daemon is running... "
if docker info &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

echo

# Check if user can run Docker without sudo
echo -n "Checking if you can run Docker without sudo... "
if docker ps &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "You may need to add your user to the docker group:"
    echo "  sudo usermod -aG docker \$USER"
    echo "Then log out and log back in to apply the changes."
    exit 1
fi

echo

# Check if platform support is available
echo -n "Checking platform support for linux/amd64... "
if docker buildx ls | grep -q "linux/amd64"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC}"
    echo "Platform linux/amd64 may not be supported. You might need to enable platform emulation."
    echo "This is required for running the Shioaji MCP server on non-amd64 systems like Apple Silicon."
fi

echo

# Test pulling a small image
echo "Testing Docker pull functionality with a small image..."
if docker pull hello-world &> /dev/null; then
    echo -e "${GREEN}Docker pull test successful${NC}"
else
    echo -e "${RED}Docker pull test failed${NC}"
    echo "Unable to pull the hello-world image. Please check your internet connection and Docker configuration."
    exit 1
fi

echo

# Test running the hello-world image
echo "Testing Docker run functionality..."
if docker run --rm hello-world | grep -q "Hello from Docker!"; then
    echo -e "${GREEN}Docker run test successful${NC}"
else
    echo -e "${RED}Docker run test failed${NC}"
    echo "Unable to run the hello-world image. Please check your Docker configuration."
    exit 1
fi

echo

# Provide instructions for Shioaji MCP
echo -e "${YELLOW}Next Steps${NC}"
echo "Your Docker setup appears to be working correctly."
echo
echo "To use the Shioaji MCP server, you can now:"
echo
echo "1. Pull the Shioaji MCP image:"
echo "   docker pull ghcr.io/musingfox/shioaji-mcp:latest"
echo
echo "2. Run the Shioaji MCP server:"
echo "   docker run --rm -i --platform=linux/amd64 \\"
echo "     -e SHIOAJI_API_KEY=your_api_key \\"
echo "     -e SHIOAJI_SECRET_KEY=your_secret_key \\"
echo "     ghcr.io/musingfox/shioaji-mcp:latest"
echo
echo "3. Configure your MCP client to use the Shioaji MCP server"
echo
echo -e "${GREEN}Setup test completed successfully!${NC}"
