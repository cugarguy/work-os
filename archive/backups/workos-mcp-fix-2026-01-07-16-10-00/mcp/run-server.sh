#!/bin/bash

# MCP Server Runner for PersonalOS
# This ensures the server runs with correct environment

cd "$(dirname "$0")/../.."
export MANAGER_AI_BASE_DIR="$(pwd)"

exec python3.11 core/mcp/server.py "$@"
