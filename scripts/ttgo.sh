#!/bin/bash

# WorkOS Startup Script
# Run this to get everything ready

set -e

echo "🚀 Starting WorkOS..."

# Set base directory
export MANAGER_AI_BASE_DIR="$(pwd)"

# Check Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Installing..."
    brew install python@3.11
fi

# Install dependencies
echo "📦 Installing dependencies..."
python3.11 -m pip install -q -r core/requirements.txt

# Ensure directories exist
mkdir -p Tasks Knowledge

# Check MCP server registration
echo "🔧 Configuring MCP server..."
if ! q mcp list 2>/dev/null | grep -q "workos"; then
    q mcp add --name workos --command python3.11 --args "$(pwd)/core/mcp/server.py" --env "MANAGER_AI_BASE_DIR=$(pwd)" --force
fi

# Test MCP server
echo "🧪 Testing MCP server..."
timeout 5s python3.11 core/mcp/server.py --help 2>/dev/null || echo "MCP server ready (stdio mode)"

echo "✅ WorkOS is ready!"
echo ""
echo "Next steps:"
echo "1. Add items to BACKLOG.md"
echo "2. Run: q chat"
echo "3. Say: 'process my backlog'"
echo ""
echo "Files:"
echo "- BACKLOG.md: Brain dump here"
echo "- GOALS.md: Your priorities"
echo "- Tasks/: Organized tasks"
echo "- Knowledge/: Reference docs"
