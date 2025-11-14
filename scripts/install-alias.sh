#!/bin/bash

# Add PersonalOS alias to shell profile

PERSONAL_OS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ALIAS_LINE="alias pos='cd $PERSONAL_OS_DIR && ./scripts/ttgo.sh'"

# Detect shell and add alias
if [[ "$SHELL" == *"zsh"* ]]; then
    PROFILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    PROFILE="$HOME/.bash_profile"
else
    PROFILE="$HOME/.profile"
fi

# Add alias if not already present
if ! grep -q "alias pos=" "$PROFILE" 2>/dev/null; then
    echo "" >> "$PROFILE"
    echo "# PersonalOS alias" >> "$PROFILE"
    echo "$ALIAS_LINE" >> "$PROFILE"
    echo "✅ Added 'pos' alias to $PROFILE"
    echo "Run 'source $PROFILE' or restart terminal to use 'pos' command"
else
    echo "✅ PersonalOS alias already exists in $PROFILE"
fi

echo ""
echo "Usage: Type 'pos' from anywhere to start PersonalOS"
