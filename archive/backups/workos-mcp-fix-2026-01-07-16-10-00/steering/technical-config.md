---
inclusion: always
---

# WorkOS Technical Configuration

## Knowledge File Access Configuration

### Primary Knowledge Store
**Location**: `knowledgebase/-common/`
**Purpose**: Consolidated knowledge repository with real-time read/write access
**Access Pattern**: Direct file system access for all knowledge operations

### Knowledge File Paths
```
Knowledge Files:
- People profiles: knowledgebase/-common/People/
- Knowledge documents: knowledgebase/-common/Topics/
- Meeting notes: knowledgebase/-common/Meetings/
- Daily notes: knowledgebase/-common/Daily/
- Context materials: knowledgebase/-common/Context/
- Templates: knowledgebase/-common/Templates/
- Resources: knowledgebase/-common/Resources/
- Tasks: knowledgebase/-common/Tasks/
- Active work: knowledgebase/-common/Active/
```

### Operational File Paths (Preserved Locally)
```
Operational Files (Local Access):
- Steering rules: 1-projects/-agents/workOS/.kiro/steering/
- Core system: 1-projects/-agents/workOS/core/
- Scripts: 1-projects/-agents/workOS/scripts/
- Documentation: 1-projects/-agents/workOS/docs/
- Configuration: 1-projects/-agents/workOS/.kiro/settings/
- Hooks: 1-projects/-agents/workOS/.kiro/hooks/
- Templates: 1-projects/-agents/workOS/core/templates/
```

## Data Access Patterns

### Reading Knowledge Files
When workOS needs to access knowledge information:
1. **Primary source**: Read from `knowledgebase/-common/[category]/`
2. **Fallback**: If file not found, check local directories for operational files
3. **Error handling**: Return clear error if knowledge file not accessible

### Writing Knowledge Files
When workOS creates new knowledge files:
1. **Target location**: Write to appropriate folder in `knowledgebase/-common/`
2. **Attribution**: Add source header "Source: workOS Agent - [YYYY-MM-DD]"
3. **File organization**: Use existing folder structure, do not create new folders

### Source Attribution Format
```markdown
<!-- Source: workOS Agent - 2025-12-19 -->
# [File Title]

[Content...]
```

## MCP Tool Integration

### Knowledge Management Tools
workOS MCP tools should access consolidated knowledgebase:
- `create_knowledge`: Write to `knowledgebase/-common/Topics/`
- `update_knowledge`: Update files in `knowledgebase/-common/Topics/`
- `search_knowledge`: Search across `knowledgebase/-common/`
- `get_related_knowledge`: Traverse wikilinks in consolidated store

### People Management Tools
workOS MCP tools should access consolidated people store:
- `create_person`: Write to `knowledgebase/-common/People/`
- `update_person`: Update files in `knowledgebase/-common/People/`
- `link_person_to_knowledge`: Link across consolidated store
- `find_expertise`: Search across consolidated people and knowledge

### Task Management Tools
workOS MCP tools should access consolidated task store:
- Task files: Write to `knowledgebase/-common/Tasks/`
- Task tracking: Update files in consolidated store
- Cross-references: Link to people and knowledge in consolidated store

## Startup Validation

### Knowledge Access Validation
On workOS startup, validate access to consolidated knowledgebase:

1. **Check directory access**: Verify `knowledgebase/-common/` is accessible
2. **Test read access**: Attempt to read a known file from each knowledge category
3. **Test write access**: Attempt to create a test file and remove it
4. **Test MCP integration**: Verify MCP tools can access consolidated store
5. **Report status**: Log validation results and any connectivity issues

### Validation Checklist
- [ ] Can read from `knowledgebase/-common/People/`
- [ ] Can read from `knowledgebase/-common/Topics/`
- [ ] Can read from `knowledgebase/-common/Daily/`
- [ ] Can read from `knowledgebase/-common/Context/`
- [ ] Can read from `knowledgebase/-common/Tasks/`
- [ ] Can write to `knowledgebase/-common/` (test file creation/deletion)
- [ ] MCP tools can access consolidated store
- [ ] Can access local operational files in `.kiro/steering/`
- [ ] Can access local operational files in `core/`
- [ ] Can access local operational files in `scripts/`

## Error Handling

### Knowledge File Access Errors
If workOS cannot access consolidated knowledge files:
1. **Log error**: Record specific path and error details
2. **User notification**: Display clear error message with resolution steps
3. **Graceful degradation**: Continue with operational files if possible
4. **Retry mechanism**: Attempt to reconnect to knowledge store

### Deprecated Path Access
If workOS attempts to access old local knowledge paths:
1. **Detect deprecated access**: Monitor for access to old local knowledge directories
2. **Return error**: Provide clear message directing to consolidated location
3. **Log attempt**: Record deprecated access attempts for monitoring
4. **Suggest migration**: Provide path to consolidated equivalent

### MCP Tool Error Handling
If MCP tools cannot access consolidated knowledge:
1. **Tool-level errors**: Return clear error messages from MCP tools
2. **Fallback behavior**: Gracefully handle missing knowledge files
3. **User guidance**: Provide specific steps to resolve access issues
4. **System status**: Report knowledge store connectivity in system status

## Cross-Agent Knowledge Sharing

### Real-time Knowledge Access
workOS shares knowledge with PM-OS through the consolidated store:
1. **Immediate visibility**: Changes written by workOS are immediately available to PM-OS
2. **Conflict resolution**: Use file timestamps and attribution for conflict detection
3. **Concurrent access**: Handle simultaneous read/write operations safely

### Knowledge File Locking
For concurrent access safety:
1. **Read operations**: No locking required (read-only access is safe)
2. **Write operations**: Use atomic file operations where possible
3. **Conflict detection**: Check file modification time before writing
4. **Merge strategy**: Preserve all content with attribution when conflicts occur

## Migration Support

### Backup Access
Original workOS knowledge files are backed up to:
- **Location**: `-Inbox/migration-backup/workos-knowledge/`
- **Structure**: Preserves original directory structure
- **Purpose**: Rollback capability and reference during transition

### Transition Period
During migration transition:
1. **Primary access**: Use consolidated knowledgebase
2. **Backup reference**: Access backup files if needed for comparison
3. **No fallback**: Do not fall back to local knowledge files
4. **Clear errors**: Provide specific guidance when old paths are accessed

## Local Knowledge Directory Deprecation

### Deprecated Directories
The following local workOS directories are deprecated for knowledge storage:
- `1-projects/-agents/workOS/Knowledge/` → Use `knowledgebase/-common/Topics/`
- `1-projects/-agents/workOS/People/` → Use `knowledgebase/-common/People/`
- `1-projects/-agents/workOS/Tasks/` → Use `knowledgebase/-common/Tasks/`
- `1-projects/-agents/workOS/daily-notes/` → Use `knowledgebase/-common/Daily/`

### Error Messages for Deprecated Access
When workOS attempts to access deprecated paths:
```
ERROR: Knowledge file access to local directory is deprecated.
Old path: 1-projects/-agents/workOS/Knowledge/[filename]
New path: knowledgebase/-common/Topics/[filename]
Please update your configuration to use the consolidated knowledgebase.
```

---

**Implementation Notes:**
- This configuration ensures workOS uses the consolidated knowledgebase for all knowledge operations
- MCP tools are updated to access the consolidated store instead of local directories
- Operational files remain in local directories to preserve agent functionality
- Cross-agent knowledge sharing is enabled through the shared consolidated store
- Startup validation ensures reliable access to knowledge files and MCP tool integration
- Error handling provides clear guidance for troubleshooting access issues
