# Scripts Directory

Setup and utility scripts for PersonalOS.

## Scripts

- **setup.sh** - Interactive setup wizard that creates your workspace and GOALS.md
- **ttgo.sh** - Main startup script that initializes dependencies and MCP server
- **install-alias.sh** - Installs a global `pos` alias for easy access from anywhere

## Usage

```bash
# First time setup
./scripts/setup.sh

# Daily startup
./scripts/ttgo.sh

# Install global alias (optional)
./scripts/install-alias.sh
```

After installing the alias, you can simply type `pos` from anywhere to start PersonalOS.
