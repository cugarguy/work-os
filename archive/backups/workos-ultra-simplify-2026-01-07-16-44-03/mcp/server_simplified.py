#!/usr/bin/env python3
"""
Simplified MCP Server for WorkOS - Essential Tools Only
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import yaml
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Import knowledge management components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from knowledge_manager import KnowledgeManager
from wikilink_resolver import WikilinkResolver
from people_manager import PeopleManager
from notes_processor import NotesProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - use environment variable or current directory
BASE_DIR = Path(os.environ.get('MANAGER_AI_BASE_DIR', Path.cwd()))
# Use consolidated knowledgebase structure
TASKS_DIR = BASE_DIR / 'knowledgebase' / '-common' / 'Tasks'

# Ensure directories exist
TASKS_DIR.mkdir(exist_ok=True, parents=True)

# Initialize knowledge management components
knowledge_manager = KnowledgeManager(BASE_DIR)
wikilink_resolver = WikilinkResolver(BASE_DIR)
people_manager = PeopleManager(BASE_DIR)
notes_processor = NotesProcessor(BASE_DIR)

def parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content
    
    try:
        parts = content.split('---', 2)[1:]
        if len(parts) >= 1:
            metadata = yaml.safe_load(parts[0])
            body = parts[1] if len(parts) > 1 else ''
            return metadata or {}, body
    except Exception as e:
        logger.error(f"Error parsing YAML: {e}")
        return {}, content

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from the consolidated Tasks directory"""
    tasks = []
    if not TASKS_DIR.exists():
        return tasks
    
    for task_file in TASKS_DIR.glob('*.md'):
        try:
            with open(task_file, 'r') as f:
                content = f.read()
                metadata, body = parse_yaml_frontmatter(content)
                if metadata:
                    metadata['filename'] = task_file.name
                    metadata['body_content'] = body[:500] if body else ''
                    tasks.append(metadata)
        except Exception as e:
            logger.error(f"Error reading {task_file}: {e}")
    
    return tasks

def update_file_frontmatter(filepath: Path, updates: dict) -> bool:
    """Update YAML frontmatter in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        metadata, body = parse_yaml_frontmatter(content)
        metadata.update(updates)
        
        # Reconstruct file
        yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_str}---\n{body}"
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        logger.error(f"Error updating {filepath}: {e}")
        return False

# Create the simplified MCP server
app = Server("workos-simplified-mcp")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools - simplified set"""
    return [
        # Task Management Tools (6)
        types.Tool(
            name="list_tasks",
            description="List tasks with optional filters (category, priority, status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (comma-separated)"},
                    "priority": {"type": "string", "description": "Filter by priority (comma-separated, e.g., P0,P1)"},
                    "status": {"type": "string", "description": "Filter by status (n,s,b,d)"},
                    "include_done": {"type": "boolean", "description": "Include completed tasks", "default": False}
                }
            }
        ),
        types.Tool(
            name="create_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "category": {"type": "string", "description": "Task category", "default": "other"},
                    "priority": {"type": "string", "description": "Priority (P0-P3)", "default": "P2"},
                    "estimated_time": {"type": "integer", "description": "Estimated time in minutes", "default": 30},
                    "content": {"type": "string", "description": "Task content/description"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="update_task_status",
            description="Update task status (n=not started, s=started, b=blocked, d=done)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_file": {"type": "string", "description": "Task filename"},
                    "status": {"type": "string", "description": "New status (n,s,b,d)"}
                },
                "required": ["task_file", "status"]
            }
        ),
        types.Tool(
            name="get_task_summary",
            description="Get summary statistics for all tasks",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="check_priority_limits",
            description="Check if priority limits are exceeded",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_system_status",
            description="Get comprehensive system status",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Notes Processing Tools (3)
        types.Tool(
            name="process_notes_inbox",
            description="Process notes from the Notes Inbox file in batch mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "notes_file": {"type": "string", "description": "Optional path to notes file (defaults to NOTES_INBOX.md)"}
                }
            }
        ),
        types.Tool(
            name="clear_backlog",
            description="Clear the backlog after processing",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="prune_completed_tasks",
            description="Delete completed tasks older than specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Days old", "default": 30}
                }
            }
        ),
        
        # Knowledge Management Tools (3)
        types.Tool(
            name="create_knowledge",
            description="Create a new knowledge document with YAML frontmatter and wikilinks",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "content": {"type": "string", "description": "Document content (markdown)"},
                    "links": {"type": "array", "items": {"type": "string"}, "description": "List of wikilinks to include", "default": []},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional list of tags", "default": []},
                    "related_people": {"type": "array", "items": {"type": "string"}, "description": "Optional list of related people (as wikilinks)", "default": []}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="update_knowledge",
            description="Update an existing knowledge document",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document identifier (filename without .md)"},
                    "updates": {
                        "type": "object",
                        "description": "Dictionary of updates to apply",
                        "properties": {
                            "content": {"type": "string", "description": "New content"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags"},
                            "related_people": {"type": "array", "items": {"type": "string"}, "description": "New related people"},
                            "time_invested": {"type": "integer", "description": "New time invested in minutes"}
                        }
                    }
                },
                "required": ["doc_id", "updates"]
            }
        ),
        types.Tool(
            name="search_knowledge",
            description="Search knowledge base using full-text search and connection ranking",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 10}
                },
                "required": ["query"]
            }
        ),
        
        # People Management Tools (3)
        types.Tool(
            name="create_person",
            description="Create a new person profile with structured metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Person's name"},
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata",
                        "properties": {
                            "role": {"type": "string", "description": "Job role/title"},
                            "team": {"type": "string", "description": "Team name"},
                            "expertise_areas": {"type": "array", "items": {"type": "string"}, "description": "List of knowledge area wikilinks"},
                            "relationships": {"type": "array", "items": {"type": "object"}, "description": "List of relationship objects"},
                            "content": {"type": "string", "description": "Profile content (markdown)"}
                        }
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="update_person",
            description="Update an existing person profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {"type": "string", "description": "Person identifier (filename without .md)"},
                    "updates": {
                        "type": "object",
                        "description": "Dictionary of updates to apply",
                        "properties": {
                            "content": {"type": "string", "description": "New content"},
                            "role": {"type": "string", "description": "New role"},
                            "team": {"type": "string", "description": "New team"},
                            "expertise_areas": {"type": "array", "items": {"type": "string"}, "description": "New expertise areas"},
                            "relationships": {"type": "array", "items": {"type": "object"}, "description": "New relationships"},
                            "total_collaboration_time": {"type": "integer", "description": "New total collaboration time in minutes"}
                        }
                    }
                },
                "required": ["person_id", "updates"]
            }
        ),
        types.Tool(
            name="link_person_to_knowledge",
            description="Create a bidirectional link between a person and a knowledge document",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {"type": "string", "description": "Person identifier (filename without .md)"},
                    "knowledge_id": {"type": "string", "description": "Knowledge document identifier (filename without .md)"},
                    "context": {"type": "string", "description": "Optional context for the link", "default": ""}
                },
                "required": ["person_id", "knowledge_id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if name == "list_tasks":
        tasks = get_all_tasks()
        
        # Apply filters
        if arguments:
            if not arguments.get('include_done', False):
                tasks = [t for t in tasks if t.get('status') != 'd']
            
            if arguments.get('category'):
                categories = [c.strip() for c in arguments['category'].split(',')]
                tasks = [t for t in tasks if t.get('category') in categories]
            
            if arguments.get('priority'):
                priorities = [p.strip() for p in arguments['priority'].split(',')]
                tasks = [t for t in tasks if t.get('priority') in priorities]
            
            if arguments.get('status'):
                statuses = [s.strip() for s in arguments['status'].split(',')]
                tasks = [t for t in tasks if t.get('status') in statuses]
        else:
            # Default: exclude done tasks
            tasks = [t for t in tasks if t.get('status') != 'd']
        
        result = {
            "tasks": tasks,
            "count": len(tasks),
            "filters_applied": arguments or {}
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_task":
        title = arguments['title']
        category = arguments.get('category', 'other')
        priority = arguments.get('priority', 'P2')
        estimated_time = arguments.get('estimated_time', 30)
        content = arguments.get('content', '')
        
        # Create filename
        filename = title.replace('/', '_').replace('\\', '_') + '.md'
        filepath = TASKS_DIR / filename
        
        # Create task metadata
        metadata = {
            'title': title,
            'category': category,
            'priority': priority,
            'status': 'n',
            'estimated_time': estimated_time,
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Create file content
        yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        file_content = f"---\n{yaml_str}---\n\n# {title}\n\n{content}"
        
        try:
            with open(filepath, 'w') as f:
                f.write(file_content)
            
            result = {
                "success": True,
                "filename": filename,
                "message": f"Task '{title}' created successfully in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_task_status":
        task_file = arguments['task_file']
        status = arguments['status']
        
        if not task_file.endswith('.md'):
            task_file += '.md'
        
        filepath = TASKS_DIR / task_file
        if not filepath.exists():
            result = {
                "success": False,
                "error": f"Task file not found: {task_file}"
            }
        else:
            success = update_file_frontmatter(filepath, {'status': status})
            status_names = {'n': 'not started', 's': 'started', 'b': 'blocked', 'd': 'done'}
            result = {
                "success": success,
                "task_file": task_file,
                "new_status": status_names.get(status, status)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_task_summary":
        tasks = get_all_tasks()
        active_tasks = [t for t in tasks if t.get('status') != 'd']
        
        from collections import Counter
        by_priority = Counter(t.get('priority', 'P2') for t in active_tasks)
        by_category = Counter(t.get('category', 'other') for t in active_tasks)
        by_status = Counter(t.get('status', 'n') for t in tasks)
        
        # Calculate time estimates
        time_by_priority = {}
        for priority in ['P0', 'P1', 'P2', 'P3']:
            priority_tasks = [t for t in active_tasks if t.get('priority') == priority]
            total_time = sum(t.get('estimated_time', 30) for t in priority_tasks)
            time_by_priority[priority] = {
                'total_minutes': total_time,
                'total_hours': round(total_time / 60, 1)
            }
        
        result = {
            "total_tasks": len(tasks),
            "active_tasks": len(active_tasks),
            "by_priority": dict(by_priority),
            "by_category": dict(by_category),
            "by_status": dict(by_status),
            "time_by_priority": time_by_priority,
            "data_source": "consolidated knowledgebase"
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "check_priority_limits":
        tasks = [t for t in get_all_tasks() if t.get('status') != 'd']
        from collections import Counter
        by_priority = Counter(t.get('priority', 'P2') for t in tasks)
        
        thresholds = {'P0': 3, 'P1': 5, 'P2': 10}
        alerts = []
        
        for priority, threshold in thresholds.items():
            count = by_priority.get(priority, 0)
            if count > threshold:
                alerts.append(f"Priority {priority}: {count} tasks (limit: {threshold})")
        
        result = {
            "overloaded": len(alerts) > 0,
            "alerts": alerts,
            "current_counts": dict(by_priority),
            "limits": thresholds
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_system_status":
        tasks = get_all_tasks()
        active_tasks = [t for t in tasks if t.get('status') != 'd']
        
        result = {
            "system": "WorkOS Simplified MCP",
            "version": "1.0",
            "data_source": "consolidated knowledgebase",
            "paths": {
                "tasks": str(TASKS_DIR),
                "knowledge": str(knowledge_manager.knowledge_dir),
                "people": str(people_manager.people_dir)
            },
            "task_counts": {
                "total": len(tasks),
                "active": len(active_tasks),
                "completed": len([t for t in tasks if t.get('status') == 'd'])
            },
            "directories_exist": {
                "tasks": TASKS_DIR.exists(),
                "knowledge": knowledge_manager.knowledge_dir.exists(),
                "people": people_manager.people_dir.exists()
            }
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_notes_inbox":
        notes_file = arguments.get('notes_file', 'NOTES_INBOX.md') if arguments else 'NOTES_INBOX.md'
        notes_path = BASE_DIR / notes_file
        
        if not notes_path.exists():
            result = {
                "success": False,
                "error": f"Notes file not found: {notes_file}"
            }
        else:
            try:
                # Use the notes processor to handle the inbox
                result = notes_processor.process_notes_inbox(str(notes_path))
                result["data_source"] = "consolidated knowledgebase"
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e)
                }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "clear_backlog":
        backlog_file = BASE_DIR / 'BACKLOG.md'
        
        try:
            with open(backlog_file, 'w') as f:
                f.write("all done!")
            
            result = {
                "success": True,
                "message": "Backlog cleared successfully"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "prune_completed_tasks":
        days = arguments.get('days', 30) if arguments else 30
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = []
        
        for task_file in TASKS_DIR.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime < cutoff_date:
                    with open(task_file, 'r') as f:
                        content = f.read()
                        metadata, _ = parse_yaml_frontmatter(content)
                        if metadata.get('status') == 'd':
                            task_file.unlink()
                            deleted.append(task_file.name)
            except Exception as e:
                logger.error(f"Error processing {task_file}: {e}")
        
        result = {
            "success": True,
            "deleted_count": len(deleted),
            "deleted_files": deleted,
            "message": f"Deleted {len(deleted)} completed tasks older than {days} days from consolidated knowledgebase"
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_knowledge":
        title = arguments['title']
        content = arguments['content']
        links = arguments.get('links', [])
        tags = arguments.get('tags', [])
        related_people = arguments.get('related_people', [])
        
        try:
            doc_path = knowledge_manager.create_knowledge(title, content, links, tags, related_people)
            result = {
                "success": True,
                "doc_path": str(doc_path),
                "message": f"Knowledge document '{title}' created successfully in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_knowledge":
        doc_id = arguments['doc_id']
        updates = arguments['updates']
        
        try:
            success = knowledge_manager.update_knowledge(doc_id, updates)
            result = {
                "success": success,
                "doc_id": doc_id,
                "message": f"Knowledge document '{doc_id}' updated successfully in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "search_knowledge":
        query = arguments['query']
        max_results = arguments.get('max_results', 10)
        
        try:
            results = knowledge_manager.search_knowledge(query, max_results)
            result = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "data_source": "consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_person":
        name = arguments['name']
        metadata = arguments.get('metadata', {})
        
        try:
            person_path = people_manager.create_person(name, metadata)
            result = {
                "success": True,
                "person_path": str(person_path),
                "message": f"Person profile '{name}' created successfully in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_person":
        person_id = arguments['person_id']
        updates = arguments['updates']
        
        try:
            success = people_manager.update_person(person_id, updates)
            result = {
                "success": success,
                "person_id": person_id,
                "message": f"Person profile '{person_id}' updated successfully in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "link_person_to_knowledge":
        person_id = arguments['person_id']
        knowledge_id = arguments['knowledge_id']
        context = arguments.get('context', '')
        
        try:
            success = people_manager.link_person_to_knowledge(person_id, knowledge_id, context)
            result = {
                "success": success,
                "person_id": person_id,
                "knowledge_id": knowledge_id,
                "message": f"Linked person '{person_id}' to knowledge '{knowledge_id}' in consolidated knowledgebase"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [types.TextContent(type="text", text=json.dumps({
            "error": f"Unknown tool: {name}"
        }, indent=2))]

if __name__ == "__main__":
    import asyncio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(main())