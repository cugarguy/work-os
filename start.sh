#!/usr/bin/env bash

# PersonalOS Q Chat Launcher with Session Resume
# Maintains conversation context across restarts

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check if session tracker exists
SESSION_FILE=".system/session_tracker.json"

if [ -f "$SESSION_FILE" ]; then
    # Extract session info
    LAST_TASK=$(grep -o '"current_task": "[^"]*"' "$SESSION_FILE" | cut -d'"' -f4)
    SESSION_ACTIVE=$(grep -o '"session_active": [^,}]*' "$SESSION_FILE" | cut -d':' -f2 | tr -d ' ')
    
    if [ "$SESSION_ACTIVE" = "true" ] && [ -n "$LAST_TASK" ]; then
        print_info "Previous session found: $LAST_TASK"
        print_success "Resuming with context..."
    else
        print_info "Starting fresh session"
    fi
else
    print_info "No previous session - starting fresh"
fi

# Launch Q with resume flag to maintain context
print_info "Launching Q Chat with session continuity..."
exec q chat --resume
