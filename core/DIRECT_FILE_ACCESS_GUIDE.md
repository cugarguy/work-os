# Direct File Access Guide for WorkOS

## Overview
With the ultra-simplified MCP server (8 tools), many operations now use direct file access for better performance and simplicity. This guide documents when to use MCP vs direct file access.

## MCP Tools (8) - Complex Business Logic Only

### Task Management (4 tools)
- `list_tasks` - Complex filtering, aggregation, business logic
- `get_task_summary` - Business intelligence, calculations, metrics
- `check_priority_limits` - Business rule validation, workload analysis
- `create_task` - YAML validation, duplicate checking, business rules

### Knowledge Management (2 tools)
- `create_knowledge` - Wikilink processing, metadata management
- `search_knowledge` - Complex search, ranking, cross-file analysis

### People Management (2 tools)
- `create_person` - Relationship management, bidirectional linking
- `link_person_to_knowledge` - Complex relationship validation

## Direct File Access Operations

### Simple Task Operations
```python
# Update task status
strReplace(task_file, old_status_line, new_status_line)

# Add progress log entry
strReplace(task_file, "## Progress Log", f"## Progress Log\n- {date}: {update}")
```

### Simple Knowledge Operations
```python
# Update knowledge content
strReplace(knowledge_file, old_content, new_content)

# Add to knowledge document
fsAppend(knowledge_file, additional_content)
```

### Simple People Operations
```python
# Update person profile
strReplace(person_file, old_info, new_info)

# Add meeting notes to person
fsAppend(person_file, f"\n## Meeting {date}\n{notes}")
```

### System Operations
```python
# Clear backlog
fsWrite("BACKLOG.md", "all done!")

# Check system status
tasks_exist = Path("knowledgebase/-common/Tasks").exists()
knowledge_exist = Path("knowledgebase/-common/Topics").exists()

# Prune old completed tasks
for task_file in tasks_dir.glob("*.md"):
    if is_old_and_completed(task_file):
        task_file.unlink()
```

### Notes Processing
```python
# Process notes inbox
with open("NOTES_INBOX.md", "r") as f:
    notes = f.read()

# Extract and process items
items = extract_items(notes)
for item in items:
    if is_task(item):
        create_task_file(item)
    elif is_knowledge(item):
        create_knowledge_file(item)

# Clear inbox
fsWrite("NOTES_INBOX.md", "")
```

## Decision Matrix

| Operation | Use MCP If | Use Direct File Access If |
|-----------|------------|---------------------------|
| Task creation | Need validation, duplicate checking | Simple task from template |
| Task updates | Complex status changes | Simple status/progress updates |
| Knowledge creation | Need wikilinks, relationships | Simple document creation |
| Knowledge updates | Complex restructuring | Simple content updates |
| People creation | Need relationship management | Simple profile creation |
| People updates | Complex relationship changes | Simple info updates |
| Search | Cross-file, ranked results | Simple file content search |
| System status | Need business metrics | Simple existence checks |
| Bulk operations | Need business logic | Simple file operations |

## Performance Benefits

### Direct File Access Advantages
- **Faster execution** - No MCP overhead
- **Simpler debugging** - Direct file operations
- **Less complexity** - No protocol translation
- **Better error handling** - Direct exception handling

### MCP Advantages (When Needed)
- **Business logic** - Complex validation and rules
- **Data integrity** - Relationship management
- **Consistency** - Standardized operations
- **Cross-references** - Wikilink processing

## Implementation Examples

### Chat Command Updates
```python
# OLD: MCP call for simple status update
mcp_workos_update_task_status(task_file, "d")

# NEW: Direct file access
strReplace(f"knowledgebase/-common/Tasks/{task_file}", 
          "status: s", "status: d")
```

### Workflow Updates
```python
# OLD: MCP call for simple backlog clear
mcp_workos_clear_backlog()

# NEW: Direct file access
fsWrite("BACKLOG.md", "all done!")
```

## Migration Guidelines

1. **Keep MCP for complex operations** that require business logic
2. **Use direct file access for simple CRUD** operations
3. **Batch simple operations** for better performance
4. **Maintain data consistency** through proper file handling
5. **Add error handling** for file operations
6. **Document operation choices** for future maintenance

---
*Updated: 2026-01-07*
*Version: Ultra-Simplified Architecture v1.0*