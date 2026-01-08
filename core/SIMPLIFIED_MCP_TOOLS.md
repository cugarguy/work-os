# WorkOS Simplified MCP Tools

## Overview
The WorkOS MCP server has been simplified from 47 tools to 15 essential tools. All tools now read/write to the consolidated knowledgebase at `knowledgebase/-common/`.

## Tool Categories

### Task Management Tools (6)
- `list_tasks` - List tasks with optional filters (category, priority, status)
- `create_task` - Create a new task in `knowledgebase/-common/Tasks/`
- `update_task_status` - Update task status (n=not started, s=started, b=blocked, d=done)
- `get_task_summary` - Get summary statistics for all tasks
- `check_priority_limits` - Check if priority limits are exceeded
- `get_system_status` - Get comprehensive system status

### Notes Processing Tools (3)
- `process_notes_inbox` - Process notes from the Notes Inbox file in batch mode
- `clear_backlog` - Clear the backlog after processing
- `prune_completed_tasks` - Delete completed tasks older than specified days

### Knowledge Management Tools (3)
- `create_knowledge` - Create a new knowledge document in `knowledgebase/-common/Topics/`
- `update_knowledge` - Update an existing knowledge document
- `search_knowledge` - Search knowledge base using full-text search

### People Management Tools (3)
- `create_person` - Create a new person profile in `knowledgebase/-common/People/`
- `update_person` - Update an existing person profile
- `link_person_to_knowledge` - Create bidirectional link between person and knowledge document

## Removed Tools (32 eliminated)
- All time tracking tools (8 tools)
- All analysis tools (4 tools)
- All parallel processing tools (5 tools)
- All session management tools (3 tools)
- Complex notes processing tools (4 tools)
- Redundant task tools (6 tools)
- Other unused tools (2 tools)

## File Path Changes
- Tasks: `BASE_DIR/Tasks/` → `knowledgebase/-common/Tasks/`
- Knowledge: `BASE_DIR/Knowledge/` → `knowledgebase/-common/Topics/`
- People: `BASE_DIR/People/` → `knowledgebase/-common/People/`

## Benefits
1. **Simplified**: Reduced from 47 to 15 tools
2. **Consolidated**: All data in single knowledgebase location
3. **Cross-agent compatible**: Shared with PM-OS through consolidated store
4. **Maintainable**: Fewer tools to maintain and debug
5. **Focused**: Only essential functionality retained

## Migration Notes
- Original MCP server backed up as `server_original_backup.py`
- All core managers updated to use consolidated paths
- MCP configuration updated with new tool list
- Requires Kiro restart to take effect

---
*Updated: 2026-01-07*
*Version: Simplified MCP v1.0*