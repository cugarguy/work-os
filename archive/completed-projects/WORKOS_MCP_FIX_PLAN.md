# WorkOS MCP Fix Plan - 2026-01-07

## Backup Status
✅ **COMPLETED** - All files backed up to `backups/workos-mcp-fix-2026-01-07-16-10-00/`

## Problem Summary
- MCP tools reading/writing to wrong file locations (local dirs instead of consolidated knowledgebase)
- 47 MCP tools (way too many, should be ~10)
- Core managers (KnowledgeManager, PeopleManager) pointing to old local directories
- Need to consolidate to use `knowledgebase/-common/` structure

## Implementation Plan

### Phase 1: Update Core Manager Classes ✅ **COMPLETED**
1. ✅ Update `core/knowledge_manager.py` - change `Knowledge/` → `knowledgebase/-common/Topics/`
2. ✅ Update `core/people_manager.py` - change `People/` → `knowledgebase/-common/People/`
3. ✅ Update `core/wikilink_resolver.py` - update search paths for consolidated structure
4. ✅ Update `core/notes_processor.py` - fix file paths for knowledge/people creation
5. ✅ Test core managers work with new paths

### Phase 2: Create Simplified MCP Server ✅ **COMPLETED**
1. ✅ Create `core/mcp/server_simplified.py` with only essential tools:
   - Task tools: `list_tasks`, `create_task`, `update_task_status`, `get_task_summary`, `check_priority_limits`, `get_system_status`
   - Notes tools: `process_notes_inbox`, `clear_backlog`, `prune_completed_tasks`
   - Knowledge tools: `create_knowledge`, `update_knowledge`, `search_knowledge`
   - People tools: `create_person`, `update_person`, `link_person_to_knowledge`
2. ✅ Update TASKS_DIR to point to `knowledgebase/-common/Tasks/`
3. ✅ Remove all time tracking, analysis, parallel processing tools (reduced from 47 to 15 tools)
4. ✅ Test simplified server works

### Phase 3: Update MCP Configuration ✅ **COMPLETED**
1. ✅ Update `.kiro/settings/mcp.json` to use simplified server
2. ✅ Update autoApprove list for new simplified tools (15 tools)
3. ✅ Test MCP server connection and tool availability (requires Kiro restart)

### Phase 4: Validation & Testing ✅ **COMPLETED**
1. ✅ Test task management tools work with consolidated knowledgebase (all working correctly)
2. ✅ Test knowledge management tools create files in correct location (verified in knowledgebase/-common/Topics/)
3. ✅ Test people management tools create files in correct location (verified in knowledgebase/-common/People/)
4. ✅ Test notes processing works with new paths (system status confirmed)
5. ✅ Verify no tools are reading from old local directories (all paths confirmed consolidated)

### Phase 5: Cleanup ✅ **COMPLETED**
1. ✅ Archive old MCP server file (renamed to server_original_backup.py)
2. ✅ Update documentation to reflect new simplified tool set (created SIMPLIFIED_MCP_TOOLS.md)
3. ✅ Remove unused dependencies if any (all current dependencies still needed)

## Key File Paths to Update
- `BASE_DIR / 'Knowledge'` → `knowledgebase/-common/Topics/`
- `BASE_DIR / 'People'` → `knowledgebase/-common/People/`
- `BASE_DIR / 'Tasks'` → `knowledgebase/-common/Tasks/`

## Tools to Keep (10 essential)
- Task: `list_tasks`, `create_task`, `update_task_status`, `get_task_summary`, `check_priority_limits`, `get_system_status`
- Notes: `process_notes_inbox`, `clear_backlog`, `prune_completed_tasks`
- Knowledge: `create_knowledge`, `update_knowledge`, `search_knowledge`
- People: `create_person`, `update_person`, `link_person_to_knowledge`

## Tools to Remove (37 tools)
- All time tracking tools (8)
- All analysis tools (4)
- All parallel processing tools (5)
- All session management tools (3)
- Complex notes processing tools (4)
- Redundant task tools (6)
- Other unused tools (7)

---
**Status**: ✅ **FULLY COMPLETE** - All phases successfully completed!
**Result**: WorkOS MCP successfully simplified and consolidated

## Final Test Results ✅
- **System Status**: Confirmed using consolidated knowledgebase paths
- **Task Management**: Successfully creates tasks in `knowledgebase/-common/Tasks/`
- **Knowledge Management**: Successfully creates documents in `knowledgebase/-common/Topics/`
- **People Management**: Successfully creates profiles in `knowledgebase/-common/People/`
- **Search Functionality**: Working correctly across consolidated knowledgebase
- **Tool Count**: Reduced from 47 to 15 tools (68% reduction)
- **Cross-Agent Compatibility**: All data now shared with PM-OS through consolidated store

## Success Metrics
- ✅ All MCP tools working correctly
- ✅ All files created in correct consolidated locations
- ✅ No tools reading from old local directories
- ✅ Significant complexity reduction (47→15 tools)
- ✅ Improved maintainability and cross-agent compatibility