#!/usr/bin/env python3
"""
Ultra-Simplified MCP Server for WorkOS - Only Essential Business Logic Tools
Reduced from 15 to 8 tools - only tools that provide genuine business value
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter

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

# Create the ultra-simplified MCP server
app = Server("workos-ultra-simple-mcp")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools - ultra-simplified set (8 essential tools only)"""
    return [
        # Task Management Tools (4) - Complex business logic only
        types.Tool(
            name="list_tasks",
            description="List tasks with complex filtering and aggregation logic",
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
            name="get_task_summary",
            description="Get summary statistics with business logic and calculations",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="check_priority_limits",
            description="Check if priority limits are exceeded using business rules",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="create_task",
            description="Create a new task with YAML frontmatter validation and business logic",
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
        
        # Knowledge Management Tools (2) - Complex processing only
        types.Tool(
            name="create_knowledge",
            description="Create knowledge document with wikilink processing and metadata management",
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
            name="search_knowledge",
            description="Search knowledge base with complex ranking and cross-file search logic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 10}
                },
                "required": ["query"]
            }
        ),
        
        # People Management Tools (2) - Relationship management only
        types.Tool(
            name="create_person",
            description="Create person profile with relationship management and validation",
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
            name="link_person_to_knowledge",
            description="Create bidirectional links with relationship validation and integrity checks",
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
    """Handle tool calls - ultra-simplified set"""
    
    if name == "list_tasks":
        tasks = get_all_tasks()
        
        # Apply complex filtering logic
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
        
        # Add complex aggregation logic
        result = {
            "tasks": tasks,
            "count": len(tasks),
            "filters_applied": arguments or {},
            "aggregations": {
                "by_priority": dict(Counter(t.get('priority', 'P2') for t in tasks)),
                "by_category": dict(Counter(t.get('category', 'other') for t in tasks)),
                "by_status": dict(Counter(t.get('status', 'n') for t in tasks))
            },
            "data_source": "consolidated knowledgebase"
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_task_summary":
        tasks = get_all_tasks()
        active_tasks = [t for t in tasks if t.get('status') != 'd']
        
        # Complex business logic and calculations
        by_priority = Counter(t.get('priority', 'P2') for t in active_tasks)
        by_category = Counter(t.get('category', 'other') for t in active_tasks)
        by_status = Counter(t.get('status', 'n') for t in tasks)
        
        # Calculate time estimates with business logic
        time_by_priority = {}
        total_estimated_time = 0
        for priority in ['P0', 'P1', 'P2', 'P3']:
            priority_tasks = [t for t in active_tasks if t.get('priority') == priority]
            total_time = sum(t.get('estimated_time', 30) for t in priority_tasks)
            total_estimated_time += total_time
            time_by_priority[priority] = {
                'total_minutes': total_time,
                'total_hours': round(total_time / 60, 1),
                'task_count': len(priority_tasks)
            }
        
        # Business intelligence calculations
        avg_time_per_task = total_estimated_time / len(active_tasks) if active_tasks else 0
        completion_rate = len([t for t in tasks if t.get('status') == 'd']) / len(tasks) if tasks else 0
        
        result = {
            "total_tasks": len(tasks),
            "active_tasks": len(active_tasks),
            "by_priority": dict(by_priority),
            "by_category": dict(by_category),
            "by_status": dict(by_status),
            "time_by_priority": time_by_priority,
            "business_metrics": {
                "total_estimated_hours": round(total_estimated_time / 60, 1),
                "avg_time_per_task_minutes": round(avg_time_per_task, 1),
                "completion_rate_percent": round(completion_rate * 100, 1)
            },
            "data_source": "consolidated knowledgebase"
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "check_priority_limits":
        tasks = [t for t in get_all_tasks() if t.get('status') != 'd']
        by_priority = Counter(t.get('priority', 'P2') for t in tasks)
        
        # Business rule validation logic
        thresholds = {'P0': 3, 'P1': 5, 'P2': 10}
        alerts = []
        recommendations = []
        
        for priority, threshold in thresholds.items():
            count = by_priority.get(priority, 0)
            if count > threshold:
                alerts.append(f"Priority {priority}: {count} tasks (limit: {threshold})")
                if priority == 'P0':
                    recommendations.append("Consider delegating or deferring some P0 tasks")
                elif priority == 'P1':
                    recommendations.append("Review P1 tasks - some may be P2 priority")
        
        # Calculate workload distribution
        total_high_priority = by_priority.get('P0', 0) + by_priority.get('P1', 0)
        total_tasks = sum(by_priority.values())
        high_priority_ratio = total_high_priority / total_tasks if total_tasks > 0 else 0
        
        result = {
            "overloaded": len(alerts) > 0,
            "alerts": alerts,
            "recommendations": recommendations,
            "current_counts": dict(by_priority),
            "limits": thresholds,
            "workload_analysis": {
                "high_priority_tasks": total_high_priority,
                "high_priority_ratio": round(high_priority_ratio, 2),
                "workload_status": "overloaded" if high_priority_ratio > 0.6 else "balanced"
            }
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_task":
        title = arguments['title']
        category = arguments.get('category', 'other')
        priority = arguments.get('priority', 'P2')
        estimated_time = arguments.get('estimated_time', 30)
        content = arguments.get('content', '')
        
        # Business logic validation
        if priority not in ['P0', 'P1', 'P2', 'P3']:
            return [types.TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Invalid priority. Must be P0, P1, P2, or P3"
            }, indent=2))]
        
        valid_categories = ['technical', 'research', 'writing', 'outreach', 'admin', 'personal', 'other']
        if category not in valid_categories:
            return [types.TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            }, indent=2))]
        
        # Create filename with validation
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = safe_title + '.md'
        filepath = TASKS_DIR / filename
        
        # Check for duplicates
        if filepath.exists():
            return [types.TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Task with title '{title}' already exists"
            }, indent=2))]
        
        # Create task metadata with validation
        metadata = {
            'title': title,
            'category': category,
            'priority': priority,
            'status': 'n',
            'estimated_time': estimated_time,
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Create file content with business logic
        yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        file_content = f"---\n{yaml_str}---\n\n# {title}\n\n{content}\n\n## Context\n[Tie to goals from GOALS.md]\n\n## Next Actions\n- [ ] [First specific action]\n\n## Progress Log\n- {datetime.now().strftime('%Y-%m-%d')}: Task created"
        
        try:
            with open(filepath, 'w') as f:
                f.write(file_content)
            
            result = {
                "success": True,
                "filename": filename,
                "message": f"Task '{title}' created successfully in consolidated knowledgebase",
                "validation": {
                    "priority_valid": True,
                    "category_valid": True,
                    "no_duplicates": True
                }
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_knowledge":
        title = arguments['title']
        content = arguments['content']
        links = arguments.get('links', [])
        tags = arguments.get('tags', [])
        related_people = arguments.get('related_people', [])
        
        try:
            # Use knowledge manager for complex wikilink processing
            doc_path = knowledge_manager.create_knowledge(title, content, links, tags, related_people)
            result = {
                "success": True,
                "doc_path": str(doc_path),
                "message": f"Knowledge document '{title}' created successfully in consolidated knowledgebase",
                "wikilinks_processed": len(links),
                "tags_added": len(tags),
                "people_linked": len(related_people)
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
            # Use knowledge manager for complex search logic
            results = knowledge_manager.search_knowledge(query, max_results)
            
            # Add search analytics
            result = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "search_analytics": {
                    "total_documents_searched": len(list(knowledge_manager.knowledge_dir.glob('*.md'))),
                    "results_returned": len(results),
                    "search_effectiveness": len(results) / max_results if max_results > 0 else 0
                },
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
            # Use people manager for complex relationship management
            person_path = people_manager.create_person(name, metadata)
            result = {
                "success": True,
                "person_path": str(person_path),
                "message": f"Person profile '{name}' created successfully in consolidated knowledgebase",
                "relationships_created": len(metadata.get('relationships', [])),
                "expertise_areas": len(metadata.get('expertise_areas', []))
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
            # Use people manager for complex bidirectional relationship logic
            success = people_manager.link_person_to_knowledge(person_id, knowledge_id, context)
            result = {
                "success": success,
                "person_id": person_id,
                "knowledge_id": knowledge_id,
                "message": f"Linked person '{person_id}' to knowledge '{knowledge_id}' in consolidated knowledgebase",
                "bidirectional": True,
                "context_added": bool(context)
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [types.TextContent(type="text", text=json.dumps({
            "error": f"Unknown tool: {name}",
            "available_tools": [
                "list_tasks", "get_task_summary", "check_priority_limits", "create_task",
                "create_knowledge", "search_knowledge", "create_person", "link_person_to_knowledge"
            ]
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