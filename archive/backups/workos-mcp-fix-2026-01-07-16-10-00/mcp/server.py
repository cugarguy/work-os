#!/usr/bin/env python3
"""
MCP Server for Manager AI - TODO System Management
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from collections import Counter

import yaml
import re
from difflib import SequenceMatcher
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import knowledge management components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from knowledge_manager import KnowledgeManager
from wikilink_resolver import WikilinkResolver
from people_manager import PeopleManager
from time_intelligence import TimeIntelligence
from notes_processor import NotesProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - use environment variable or current directory
BASE_DIR = Path(os.environ.get('MANAGER_AI_BASE_DIR', Path.cwd()))
TASKS_DIR = BASE_DIR / 'Tasks'

# Ensure directories exist
TASKS_DIR.mkdir(exist_ok=True, parents=True)

# Initialize knowledge management components
knowledge_manager = KnowledgeManager(BASE_DIR)
wikilink_resolver = WikilinkResolver(BASE_DIR)
people_manager = PeopleManager(BASE_DIR)
time_intelligence = TimeIntelligence(BASE_DIR)
notes_processor = NotesProcessor(BASE_DIR)

# Duplicate detection configuration
DEDUP_CONFIG = {
    "similarity_threshold": 0.6,  # How similar before flagging as potential duplicate
    "check_categories": True,     # Same category increases similarity score
}

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
    """Get all tasks from the Tasks directory"""
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

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two strings (0-1 score)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text"""
    # Remove common words and extract meaningful terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'from', 'up', 'out'}
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if w not in stop_words and len(w) > 2}

def find_similar_tasks(item: str, existing_tasks: List[Dict[str, Any]], config: dict = DEDUP_CONFIG) -> List[Dict[str, Any]]:
    """Find tasks similar to the given item"""
    similar = []
    item_keywords = extract_keywords(item)
    
    for task in existing_tasks:
        # Skip completed tasks
        if task.get('status') == 'd':
            continue
            
        # Calculate title similarity
        title = task.get('title', '')
        title_similarity = calculate_similarity(item, title)
        
        # Calculate keyword overlap
        task_keywords = extract_keywords(title)
        if item_keywords and task_keywords:
            keyword_overlap = len(item_keywords & task_keywords) / len(item_keywords | task_keywords)
        else:
            keyword_overlap = 0
        
        # Combined score
        similarity_score = (title_similarity * 0.7) + (keyword_overlap * 0.3)
        
        # Check if it's a potential duplicate
        if similarity_score >= config['similarity_threshold']:
            similar.append({
                'title': title,
                'filename': task.get('filename', ''),
                'category': task.get('category', ''),
                'status': task.get('status', ''),
                'similarity_score': round(similarity_score, 2)
            })
    
    # Sort by similarity score
    similar.sort(key=lambda x: x['similarity_score'], reverse=True)
    return similar[:3]  # Return top 3 matches

def is_ambiguous(item: str) -> bool:
    """Check if an item is too vague or ambiguous"""
    vague_patterns = [
        r'^(fix|update|improve|check|review|look at|work on)\s+(the|a|an)?\s*\w+$',  # "fix bug", "update docs"
        r'^\w+\s+(stuff|thing|issue|problem)$',  # "database stuff", "API thing"
        r'^(follow up|reach out|contact|email)$',  # Missing who/what
        r'^(investigate|research|explore)\s*\w{0,20}$',  # Too broad
    ]
    
    item_lower = item.lower().strip()
    
    # Check if too short
    if len(item_lower.split()) <= 2:
        return True
    
    # Check vague patterns
    for pattern in vague_patterns:
        if re.match(pattern, item_lower):
            return True
    
    return False

def generate_clarification_questions(item: str) -> List[str]:
    """Generate clarification questions for ambiguous items"""
    questions = []
    item_lower = item.lower()
    
    # Technical ambiguity
    if any(word in item_lower for word in ['fix', 'bug', 'error', 'issue']):
        questions.append("Which specific bug or error? Can you provide more details or error messages?")
        questions.append("What component or feature is affected?")
    
    # Scope ambiguity
    if any(word in item_lower for word in ['update', 'improve', 'refactor']):
        questions.append("What specific aspects need updating/improvement?")
        questions.append("What's the success criteria for this task?")
    
    # Missing target
    if any(word in item_lower for word in ['email', 'contact', 'reach out', 'follow up']):
        questions.append("Who should be contacted?")
        questions.append("What's the purpose or goal of this outreach?")
    
    # Missing context
    if any(word in item_lower for word in ['research', 'investigate', 'explore']):
        questions.append("What specific questions need to be answered?")
        questions.append("What decisions will this research inform?")
    
    # Generic catch-all
    if not questions:
        questions.append("Can you provide more specific details about what needs to be done?")
        questions.append("What's the expected outcome or deliverable?")
    
    return questions

def guess_category(item: str) -> str:
    """Guess the category based on item text"""
    item_lower = item.lower()
    
    # Check for category indicators
    if any(word in item_lower for word in ['email', 'contact', 'reach out', 'follow up', 'meeting', 'call']):
        return 'outreach'
    elif any(word in item_lower for word in ['code', 'api', 'database', 'deploy', 'fix', 'bug', 'implement']):
        return 'technical'
    elif any(word in item_lower for word in ['research', 'study', 'learn', 'understand', 'investigate']):
        return 'research'
    elif any(word in item_lower for word in ['write', 'draft', 'document', 'blog', 'article', 'proposal']):
        return 'writing'
    elif any(word in item_lower for word in ['expense', 'invoice', 'schedule', 'calendar', 'organize']):
        return 'admin'
    elif any(word in item_lower for word in ['tweet', 'post', 'linkedin', 'social', 'twitter', 'marketing', 'blog']):
        return 'marketing'
    else:
        return 'other'

def classify_backlog_content(content: str) -> dict:
    """Classify backlog content into different types"""
    sections = content.split('---')
    
    result = {
        'notes': [],
        'tasks': [],
        'reminders': [],
        'meeting_notes': [],
        'ideas': [],
        'other': []
    }
    
    for section in sections:
        section = section.strip()
        if not section or section == 'all done!':
            continue
            
        # Identify section type based on content patterns
        section_lower = section.lower()
        
        if any(keyword in section_lower for keyword in ['notes for', 'notes about', 'notes on']):
            result['notes'].append({
                'content': section,
                'suggested_location': 'Knowledge/',
                'type': 'reference_notes'
            })
        elif any(keyword in section_lower for keyword in ['review', 'meeting', 'discussion', 'we ', 'they ']):
            result['meeting_notes'].append({
                'content': section,
                'suggested_location': 'Knowledge/',
                'type': 'meeting_notes'
            })
        elif any(keyword in section_lower for keyword in ['todo', '- [ ]', 'need to', 'should ', 'must ']):
            # Extract actual tasks
            lines = section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or 'need to' in line.lower() or 'should' in line.lower():
                    result['tasks'].append({
                        'content': line,
                        'suggested_category': guess_category(line),
                        'type': 'actionable_task'
                    })
        elif any(keyword in section_lower for keyword in ['remember', 'remind', 'follow up', 'check with']):
            result['reminders'].append({
                'content': section,
                'type': 'reminder'
            })
        elif any(keyword in section_lower for keyword in ['idea', 'what if', 'maybe', 'could']):
            result['ideas'].append({
                'content': section,
                'suggested_location': 'Knowledge/',
                'type': 'idea'
            })
        else:
            result['other'].append({
                'content': section,
                'type': 'unclassified'
            })
    
    return result

def update_session_tracker(current_task: str = None, status: str = None, notes: str = None, next_action: str = None):
    """Update session tracking file"""
    session_file = BASE_DIR / '.system' / 'session_tracker.json'
    
    session_data = {
        'last_updated': datetime.now().isoformat(),
        'current_task': current_task,
        'status': status,
        'notes': notes,
        'next_action': next_action,
        'day': datetime.now().strftime('%Y-%m-%d'),
        'session_active': status not in ['completed', 'ended', None]
    }
    
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error updating session tracker: {e}")
        return False

def get_session_tracker() -> dict:
    """Get current session tracking data"""
    session_file = BASE_DIR / '.system' / 'session_tracker.json'
    
    if not session_file.exists():
        return {
            'session_active': False,
            'message': 'No previous session found'
        }
    
    try:
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        # Check if session is from today
        last_day = data.get('day')
        today = datetime.now().strftime('%Y-%m-%d')
        
        if last_day != today:
            data['session_active'] = False
            data['message'] = f'Last session was {last_day}, starting fresh for {today}'
        
        return data
    except Exception as e:
        logger.error(f"Error reading session tracker: {e}")
        return {
            'session_active': False,
            'error': str(e)
        }
    """Suggest a filename for knowledge content"""
    # Extract key terms from the first line or header
    first_line = content.split('\n')[0].strip()
    
    # Remove common prefixes
    for prefix in ['**Notes for', '**Notes about', '**Notes on', 'Notes for', 'Notes about']:
        if first_line.startswith(prefix):
            first_line = first_line.replace(prefix, '').strip('*: ')
            break
    
    # Clean and format filename
    filename = re.sub(r'[^\w\s-]', '', first_line)
    filename = re.sub(r'[-\s]+', '-', filename)
    filename = filename.strip('-').lower()
    
    return f"{filename}.md" if filename else "notes.md"
    """Generate rich task content based on item and category"""
    
    # Base structure that all tasks get
    base_content = f"""## Overview
{get_task_overview(item, category)}

## Next Actions
{get_next_actions(item, category)}

## Notes & Details
- Task created from backlog processing
- Category: {category}
"""
    
    # Add category-specific sections
    if category == 'outreach':
        base_content += """
## Draft Message
[Draft outreach message here based on context]

## Contact Details
- LinkedIn profile: [to be added]
- Email: [to be added]
"""
    elif category == 'writing':
        base_content += """
## Key Points
- [Main argument or thesis]
- [Supporting points]
- [Call to action]

## Target Audience
[Define who this is for]

## Resources
- [Related documents or references]
"""
    elif category == 'technical':
        base_content += """
## Technical Requirements
- [Specific technical details]
- [Dependencies or prerequisites]
- [Expected outcome]

## Implementation Notes
- [Technical approach]
- [Testing considerations]
"""
    elif category == 'research':
        base_content += """
## Research Questions
- [What are we trying to learn?]
- [Key hypotheses to test]

## Sources to Explore
- [Relevant resources]
- [People to consult]
"""
    elif category == 'marketing':
        base_content += """
## Content Strategy
- Platform: [Twitter/LinkedIn/Blog/etc]
- Key message: [Core point]
- Engagement goal: [What response do we want?]

## Draft Post
[Initial draft of marketing content]
"""
        
    return base_content

def get_task_overview(item: str, category: str) -> str:
    """Generate a contextual overview based on the task"""
    item_lower = item.lower()
    
    # Provide smarter overviews based on keywords
    if 'proposal' in item_lower:
        return f"Create and submit a comprehensive proposal for {item}. Research requirements, draft content, and prepare supporting materials."
    elif 'review' in item_lower:
        return f"Conduct thorough review of {item}. Provide feedback, suggestions, and actionable improvements."
    elif 'follow up' in item_lower or 'reach out' in item_lower:
        return f"Establish or continue communication regarding {item}. Ensure clear next steps and maintain relationship momentum."
    elif 'post' in item_lower or 'write' in item_lower:
        return f"Create compelling content for {item}. Focus on value delivery and audience engagement."
    elif 'implement' in item_lower or 'build' in item_lower:
        return f"Design and implement solution for {item}. Ensure functionality, testing, and documentation."
    else:
        return f"Complete {item} with focus on quality and timeliness."

def get_next_actions(item: str, category: str) -> str:
    """Generate smart next actions based on task type"""
    actions = []
    
    # Universal first steps
    actions.append("- [ ] Review related context and existing work")
    
    # Category-specific actions
    if category == 'outreach':
        actions.extend([
            "- [ ] Research contact's recent activity/interests",
            "- [ ] Draft personalized message",
            "- [ ] Schedule follow-up reminder"
        ])
    elif category == 'writing':
        actions.extend([
            "- [ ] Create outline with key points",
            "- [ ] Write first draft",
            "- [ ] Review and edit for clarity",
            "- [ ] Prepare for publication/submission"
        ])
    elif category == 'technical':
        actions.extend([
            "- [ ] Define technical requirements",
            "- [ ] Set up development environment",
            "- [ ] Implement core functionality",
            "- [ ] Test and validate solution"
        ])
    elif category == 'research':
        actions.extend([
            "- [ ] Define research questions",
            "- [ ] Gather relevant sources",
            "- [ ] Analyze and synthesize findings",
            "- [ ] Document insights and recommendations"
        ])
    elif category == 'marketing':
        actions.extend([
            "- [ ] Research trending topics/hashtags",
            "- [ ] Draft engaging content",
            "- [ ] Add relevant visuals/links",
            "- [ ] Schedule optimal posting time"
        ])
    else:
        actions.extend([
            "- [ ] Define specific requirements",
            "- [ ] Create action plan",
            "- [ ] Execute plan",
            "- [ ] Verify completion"
        ])
    
    return '\n'.join(actions)

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

def save_time_entry(category: str, work_completed: str, time_spent: int, completion_percentage: float = None):
    """Save time tracking entry to analytics file"""
    analytics_file = BASE_DIR / 'time_analytics.json'
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'category': category,
        'work_completed': work_completed,
        'time_spent': time_spent,
        'completion_percentage': completion_percentage
    }
    
    try:
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'entries': []}
        
        data['entries'].append(entry)
        
        with open(analytics_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving time entry: {e}")
        return False

def save_distraction_entry(task_category: str, distractions: str, distraction_time: int, task_title: str = None):
    """Save distraction tracking entry to analytics file"""
    distractions_file = BASE_DIR / 'distraction_analytics.json'
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'task_category': task_category,
        'task_title': task_title,
        'distractions': distractions,
        'distraction_time': distraction_time,
        'day_of_week': datetime.now().strftime('%A'),
        'hour': datetime.now().hour
    }
    
    try:
        if distractions_file.exists():
            with open(distractions_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'entries': []}
        
        data['entries'].append(entry)
        
        with open(distractions_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving distraction entry: {e}")
        return False

def get_distraction_analytics(days: int = 30) -> dict:
    """Get distraction analytics from historical data"""
    distractions_file = BASE_DIR / 'distraction_analytics.json'
    
    if not distractions_file.exists():
        return {'entries': [], 'stats': {}}
    
    try:
        with open(distractions_file, 'r') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter by date
        filtered_entries = []
        for entry in entries:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if entry_date >= cutoff_date:
                filtered_entries.append(entry)
        
        # Calculate stats
        if filtered_entries:
            times = [e['distraction_time'] for e in filtered_entries]
            by_category = Counter(e['task_category'] for e in filtered_entries)
            by_day = Counter(e['day_of_week'] for e in filtered_entries)
            by_hour = Counter(e['hour'] for e in filtered_entries)
            
            # Common distraction patterns
            distraction_types = []
            for entry in filtered_entries:
                distraction_types.extend([d.strip().lower() for d in entry['distractions'].split(',')])
            common_distractions = Counter(distraction_types).most_common(5)
            
            stats = {
                'total_entries': len(filtered_entries),
                'total_distraction_time': sum(times),
                'avg_distraction_time': sum(times) / len(times),
                'by_task_category': dict(by_category),
                'by_day_of_week': dict(by_day),
                'by_hour': dict(by_hour),
                'common_distractions': common_distractions
            }
        else:
            stats = {}
        
        return {'entries': filtered_entries, 'stats': stats}
    
    except Exception as e:
        logger.error(f"Error reading distraction analytics: {e}")
        return {'entries': [], 'stats': {}}
    """Get time analytics from historical data"""
    analytics_file = BASE_DIR / 'time_analytics.json'
    
    if not analytics_file.exists():
        return {'entries': [], 'stats': {}}
    
    try:
        with open(analytics_file, 'r') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter by date and category
        filtered_entries = []
        for entry in entries:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if entry_date >= cutoff_date:
                if not category or entry.get('category') == category:
                    filtered_entries.append(entry)
        
        # Calculate stats
        if filtered_entries:
            times = [e['time_spent'] for e in filtered_entries]
            by_category = {}
            
            for entry in filtered_entries:
                cat = entry.get('category', 'other')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(entry['time_spent'])
            
            stats = {
                'total_entries': len(filtered_entries),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'by_category': {
                    cat: {
                        'avg': sum(times) / len(times),
                        'count': len(times)
                    }
                    for cat, times in by_category.items()
                }
            }
        else:
            stats = {}
        
        return {'entries': filtered_entries, 'stats': stats}
    
    except Exception as e:
        logger.error(f"Error reading analytics: {e}")
        return {'entries': [], 'stats': {}}

# Create the MCP server
app = Server("manager-ai-mcp")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools"""
    return [
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
        types.Tool(
            name="process_backlog",
            description="[DEPRECATED] Use process_notes_inbox instead. Read and return backlog contents",
            inputSchema={"type": "object", "properties": {}}
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
        types.Tool(
            name="process_backlog_with_dedup",
            description="Process backlog items with duplicate detection and clarification",
            inputSchema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of backlog items to process"
                    },
                    "auto_create": {
                        "type": "boolean",
                        "description": "Automatically create non-duplicate tasks",
                        "default": False
                    }
                },
                "required": ["items"]
            }
        ),
        types.Tool(
            name="daily_checkin",
            description="Interactive check-in for task progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_updates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task_file": {"type": "string"},
                                "completed": {"type": "boolean"},
                                "worked_on": {"type": "boolean"},
                                "work_completed": {"type": "string"},
                                "time_spent": {"type": "integer"},
                                "next_step": {"type": "string"},
                                "had_distractions": {"type": "boolean"},
                                "distractions": {"type": "string"},
                                "distraction_time": {"type": "integer"}
                            },
                            "required": ["task_file"]
                        },
                        "description": "Array of task updates from check-in"
                    }
                }
            }
        ),
        types.Tool(
            name="get_time_estimates",
            description="Get time estimates for tasks based on historical data",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Task category to get estimates for"},
                    "task_description": {"type": "string", "description": "Description of new task to estimate"}
                }
            }
        ),
        types.Tool(
            name="view_time_analytics",
            description="View time tracking analytics and patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category"},
                    "days": {"type": "integer", "description": "Days of history to analyze", "default": 30}
                }
            }
        ),
        types.Tool(
            name="view_distraction_analytics",
            description="View distraction patterns and analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Days of history to analyze", "default": 30}
                }
            }
        ),
        types.Tool(
            name="process_backlog_smart",
            description="Intelligently process backlog into notes, tasks, reminders, and ideas",
            inputSchema={
                "type": "object",
                "properties": {
                    "auto_save_notes": {"type": "boolean", "description": "Automatically save notes to Knowledge/", "default": False},
                    "auto_create_tasks": {"type": "boolean", "description": "Automatically create identified tasks", "default": False}
                }
            }
        ),
        types.Tool(
            name="update_session",
            description="Update current session context and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_task": {"type": "string", "description": "Task currently being worked on"},
                    "status": {"type": "string", "description": "Current status (working, paused, completed, blocked)"},
                    "notes": {"type": "string", "description": "Session notes or context"},
                    "next_action": {"type": "string", "description": "What to do next"}
                }
            }
        ),
        types.Tool(
            name="get_session_status",
            description="Get current session status and last context",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="end_session",
            description="End current session with summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Session summary"},
                    "completed_tasks": {"type": "array", "items": {"type": "string"}, "description": "Tasks completed this session"},
                    "next_session_plan": {"type": "string", "description": "Plan for next session"}
                }
            }
        ),
        types.Tool(
            name="prepare_parallel_backlog_processing",
            description="Prepare backlog items for parallel delegate processing - returns structured data for delegates",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_existing_tasks": {"type": "boolean", "description": "Include existing tasks context", "default": True}
                }
            }
        ),
        types.Tool(
            name="prepare_parallel_task_analysis",
            description="Prepare task data for parallel analysis by delegates - returns tasks grouped for parallel processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Types of analysis: priority, category, blockers, goal_alignment, time_estimates"
                    }
                }
            }
        ),
        types.Tool(
            name="prepare_parallel_daily_planning",
            description="Prepare data for parallel daily planning delegates - returns context for smart task recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_goals": {"type": "boolean", "description": "Include goals context", "default": True},
                    "include_knowledge": {"type": "boolean", "description": "Include knowledge base context", "default": False}
                }
            }
        ),
        types.Tool(
            name="aggregate_parallel_results",
            description="Aggregate results from parallel delegate operations and take final actions",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation_type": {"type": "string", "description": "Type: backlog_processing, task_analysis, daily_planning"},
                    "delegate_results": {"type": "array", "items": {"type": "object"}, "description": "Results from delegates"},
                    "auto_create_tasks": {"type": "boolean", "description": "Auto-create tasks from backlog results", "default": False}
                }
            }
        ),
        # Knowledge Management Tools
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
        types.Tool(
            name="get_related_knowledge",
            description="Get related knowledge documents by traversing the wikilink graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document identifier (filename without .md)"},
                    "depth": {"type": "integer", "description": "How many levels deep to traverse", "default": 1}
                },
                "required": ["doc_id"]
            }
        ),
        types.Tool(
            name="validate_wikilinks",
            description="Validate all wikilinks in a document and identify broken links",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document identifier (filename without .md), or omit to validate all documents"},
                },
            }
        ),
        # People Management Tools
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
        ),
        types.Tool(
            name="link_people",
            description="Create a relationship link between two people",
            inputSchema={
                "type": "object",
                "properties": {
                    "person1_id": {"type": "string", "description": "First person identifier (filename without .md)"},
                    "person2_id": {"type": "string", "description": "Second person identifier (filename without .md)"},
                    "relationship": {"type": "string", "description": "Type of relationship (e.g., 'collaborator', 'reports_to', 'manager')"},
                    "context": {"type": "string", "description": "Optional context describing the relationship", "default": ""}
                },
                "required": ["person1_id", "person2_id", "relationship"]
            }
        ),
        types.Tool(
            name="find_expertise",
            description="Find people with expertise in a given topic by searching knowledge connections",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic or knowledge area to search for"}
                },
                "required": ["topic"]
            }
        ),
        # Time Tracking Tools
        types.Tool(
            name="start_work",
            description="Start tracking work time with description, type, and optional knowledge/people references",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Description of the work being performed"},
                    "work_type": {"type": "string", "description": "Type/category of work (e.g., 'technical', 'writing', 'meeting')", "default": "general"},
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}, "description": "List of related knowledge document names"},
                    "people_refs": {"type": "array", "items": {"type": "string"}, "description": "List of related people names"}
                },
                "required": ["description"]
            }
        ),
        types.Tool(
            name="end_work",
            description="End work tracking and calculate duration",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_id": {"type": "string", "description": "Unique identifier of the work entry"},
                    "completion_notes": {"type": "string", "description": "Notes about work completion", "default": ""},
                    "completion_percentage": {"type": "integer", "description": "Percentage of work completed (0-100)"}
                },
                "required": ["work_id"]
            }
        ),
        types.Tool(
            name="record_distraction",
            description="Record a distraction event during work",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_id": {"type": "string", "description": "Unique identifier of the work entry"},
                    "distraction_type": {"type": "string", "description": "Type of distraction (e.g., 'meeting', 'interruption', 'email')"},
                    "duration_minutes": {"type": "integer", "description": "Duration of the distraction in minutes"},
                    "description": {"type": "string", "description": "Optional description of the distraction", "default": ""}
                },
                "required": ["work_id", "distraction_type", "duration_minutes"]
            }
        ),
        types.Tool(
            name="get_time_history",
            description="Get time history with optional filters by work type, knowledge area, or person",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_type": {"type": "string", "description": "Filter by work type"},
                    "knowledge_ref": {"type": "string", "description": "Filter by knowledge document name"},
                    "person_ref": {"type": "string", "description": "Filter by person name"},
                    "days": {"type": "integer", "description": "Number of days to look back", "default": 30}
                }
            }
        ),
        types.Tool(
            name="get_time_estimate",
            description="Get time estimate for work based on historical patterns, with optional distraction and experience adjustments",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_description": {"type": "string", "description": "Description of the work to estimate"},
                    "work_type": {"type": "string", "description": "Type of work"},
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}, "description": "List of related knowledge document names"},
                    "people_refs": {"type": "array", "items": {"type": "string"}, "description": "List of people involved (for collaboration adjustment)"},
                    "include_distraction_overhead": {"type": "boolean", "description": "Factor in typical distraction overhead", "default": False},
                    "adjust_for_experience": {"type": "boolean", "description": "Adjust estimate based on experience level in knowledge areas", "default": False},
                    "adjust_for_collaboration": {"type": "boolean", "description": "Adjust estimate based on collaboration history with specified people", "default": False}
                },
                "required": ["work_description", "work_type"]
            }
        ),
        types.Tool(
            name="suggest_work_breakdown",
            description="Suggest a logical breakdown of work into smaller chunks with estimates",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_description": {"type": "string", "description": "Description of the work to break down"},
                    "work_type": {"type": "string", "description": "Type of work"},
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}, "description": "List of related knowledge document names"},
                    "accept_breakdown": {"type": "boolean", "description": "Automatically accept and create time entries for chunks", "default": False}
                },
                "required": ["work_description", "work_type"]
            }
        ),
        # Notes Processing Tools
        types.Tool(
            name="process_notes_inbox",
            description="Process notes from the Notes Inbox file in batch mode. Extracts entities, creates/updates knowledge and people documents, then clears the inbox.",
            inputSchema={
                "type": "object",
                "properties": {
                    "notes_file": {"type": "string", "description": "Optional path to notes file (defaults to NOTES_INBOX.md)"}
                }
            }
        ),
        types.Tool(
            name="process_notes_interactive",
            description="Start an interactive notes processing session. Presents notes one at a time, asks clarifying questions, and waits for user confirmation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "notes_file": {"type": "string", "description": "Optional path to notes file (defaults to NOTES_INBOX.md)"}
                }
            }
        ),
        types.Tool(
            name="process_interactive_note",
            description="Process the next note in an interactive session. Extracts entities, detects ambiguities, and generates clarification questions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "The interactive session ID"},
                    "clarifications": {"type": "object", "description": "Optional clarifications from previous questions"},
                    "confirmed": {"type": "boolean", "description": "Whether to confirm and apply updates", "default": False},
                    "advance": {"type": "boolean", "description": "Whether to advance to next note", "default": False}
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="process_conversational_note",
            description="Process a note from real-time conversation. Analyzes content, detects entities, asks clarifying questions, and proposes updates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_text": {"type": "string", "description": "The note text from conversation"},
                    "context": {"type": "object", "description": "Optional context from previous conversation turns"},
                    "apply_updates": {"type": "boolean", "description": "Whether to apply proposed updates", "default": False},
                    "proposed_updates": {"type": "array", "description": "Proposed updates to apply (if apply_updates is true)"}
                },
                "required": ["note_text"]
            }
        ),
        types.Tool(
            name="process_meeting_notes",
            description="Process meeting notes with attendees and topics. Extracts knowledge, updates person profiles, and creates connections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendee names"},
                    "topics": {"type": "array", "items": {"type": "string"}, "description": "List of topics discussed"},
                    "notes": {"type": "string", "description": "Meeting notes text"},
                    "date": {"type": "string", "description": "Meeting date (ISO format)"}
                },
                "required": ["attendees", "topics", "notes"]
            }
        ),
        # Analysis Tools
        types.Tool(
            name="get_distraction_analysis",
            description="Analyze distraction patterns by time of day, day of week, and work type. Identifies when distractions occur most frequently and calculates their impact on work duration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to analyze (default: all time)"},
                    "work_type": {"type": "string", "description": "Filter by specific work type (default: all types)"},
                    "include_impact": {"type": "boolean", "description": "Include distraction impact calculation (default: true)", "default": True}
                }
            }
        ),
        types.Tool(
            name="get_expertise_analysis",
            description="Analyze expertise by ranking knowledge areas by time investment. Shows which topics have received the most time and attention.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_minutes": {"type": "integer", "description": "Minimum time threshold in minutes (default: 60)", "default": 60}
                }
            }
        ),
        types.Tool(
            name="get_collaboration_analysis",
            description="Identify frequent collaborators and collaboration patterns. Shows who you work with most, collaboration time by work type, and solo vs collaborative work breakdown.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to analyze (default: all time)"}
                }
            }
        ),
        types.Tool(
            name="get_time_trends",
            description="Get time trends grouped by knowledge area over time. Shows how time investment in different topics changes over time periods.",
            inputSchema={
                "type": "object",
                "properties": {
                    "knowledge_ref": {"type": "string", "description": "Specific knowledge area to analyze (default: all areas)"},
                    "days": {"type": "integer", "description": "Number of days to analyze (default: 90)", "default": 90},
                    "group_by": {"type": "string", "description": "Grouping period: 'day', 'week', or 'month' (default: 'week')", "default": "week"}
                }
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
            'estimated_time': estimated_time
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
                "message": f"Task '{title}' created successfully"
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
            "time_by_priority": time_by_priority
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "check_priority_limits":
        tasks = [t for t in get_all_tasks() if t.get('status') != 'd']
        by_priority = Counter(t.get('priority', 'P2') for t in tasks)
        
        thresholds = {'P0': 3, 'P1': 5, 'P2': 10}
        alerts = []
        
        for priority, threshold in thresholds.items():
            count = by_priority.get(priority, 0)
            if count > threshold:
                alerts.append(f"{priority} has {count} tasks (limit: {threshold})")
        
        result = {
            "priority_counts": dict(by_priority),
            "alerts": alerts,
            "balanced": len(alerts) == 0
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_system_status":
        all_tasks = get_all_tasks()
        active_tasks = [t for t in all_tasks if t.get('status') != 'd']

        priority_counts = Counter(task['priority'] for task in active_tasks)
        status_counts = Counter(task['status'] for task in active_tasks)
        category_counts = Counter(task['category'] for task in active_tasks)

        # Check backlog
        backlog_items = 0
        backlog_file = BASE_DIR / 'BACKLOG.md'
        if backlog_file.exists():
            with open(backlog_file, 'r') as f:
                content = f.read().strip()
                if content and content != 'all done!':
                    backlog_items = len([l for l in content.split('\n') if l.strip().startswith('-')])

        # Time insights
        now = datetime.now()
        hour = now.hour
        day_name = now.strftime('%A')

        time_insights = []
        if 9 <= hour < 12:
            time_insights.append("Morning - ideal for outreach tasks")
        elif 14 <= hour < 17:
            time_insights.append("Afternoon - good for deep work")
        elif hour >= 17:
            time_insights.append("End of day - quick admin tasks")

        result = {
            "total_active_tasks": len(active_tasks),
            "priority_distribution": dict(priority_counts),
            "status_distribution": dict(status_counts),
            "category_distribution": dict(category_counts),
            "backlog_items": backlog_items,
            "time_insights": time_insights,
            "timestamp": now.isoformat()
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_backlog":
        backlog_file = BASE_DIR / 'BACKLOG.md'
        
        if not backlog_file.exists():
            result = {
                "success": False,
                "error": "BACKLOG.md not found"
            }
        else:
            with open(backlog_file, 'r') as f:
                content = f.read().strip()
            
            if not content or content == 'all done!':
                result = {
                    "success": True,
                    "content": None,
                    "message": "Backlog is already clear"
                }
            else:
                # Parse items
                lines = content.split('\n')
                items = []
                current_item = None
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('- '):
                        if current_item:
                            items.append(current_item)
                        current_item = {
                            'text': stripped[2:],
                            'subitems': []
                        }
                    elif stripped.startswith('  - ') and current_item:
                        current_item['subitems'].append(stripped[4:])
                
                if current_item:
                    items.append(current_item)
                
                result = {
                    "success": True,
                    "content": content,
                    "parsed_items": items,
                    "count": len(items)
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
            "message": f"Deleted {len(deleted)} tasks older than {days} days"
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_backlog_with_dedup":
        items = arguments.get('items', [])
        auto_create = arguments.get('auto_create', False)
        
        if not items:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "No items provided to process"
            }, indent=2))]

        existing_tasks = get_all_tasks()

        result = {
            "new_tasks": [],
            "potential_duplicates": [],
            "needs_clarification": [],
            "auto_created": [],
            "summary": {}
        }
        
        for item in items:
            # Check for duplicates
            similar_tasks = find_similar_tasks(item, existing_tasks)
            
            if similar_tasks:
                result["potential_duplicates"].append({
                    "item": item,
                    "similar_tasks": similar_tasks,
                    "recommended_action": "merge" if similar_tasks[0]['similarity_score'] > 0.8 else "review"
                })
            elif is_ambiguous(item):
                result["needs_clarification"].append({
                    "item": item,
                    "questions": generate_clarification_questions(item),
                    "suggestions": [
                        "Add more specific details",
                        "Include success criteria",
                        "Specify scope or boundaries"
                    ]
                })
            else:
                # This is a new, clear task
                result["new_tasks"].append({
                    "item": item,
                    "suggested_category": guess_category(item),
                    "suggested_priority": "P2",  # Default priority
                    "ready_to_create": True
                })
                
                # Auto-create if requested
                if auto_create:
                    # Create the task file
                    safe_filename = re.sub(r'[^\w\s-]', '', item).strip()
                    safe_filename = re.sub(r'[-\s]+', ' ', safe_filename)
                    task_file = TASKS_DIR / f"{safe_filename}.md"
                    
                    metadata = {
                        "title": item,
                        "category": guess_category(item),
                        "priority": "P2",
                        "status": "n",
                        "estimated_time": 60
                    }
                    
                    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
                    
                    # Generate richer task content based on category
                    task_content = generate_task_content(item, metadata['category'])
                    content = f"---\n{yaml_str}---\n\n# {item}\n\n{task_content}"
                    
                    with open(task_file, 'w') as f:
                        f.write(content)
                    
                    result["auto_created"].append(safe_filename + ".md")
        
        # Add summary
        result["summary"] = {
            "total_items": len(items),
            "new_tasks": len(result["new_tasks"]),
            "duplicates_found": len(result["potential_duplicates"]),
            "needs_clarification": len(result["needs_clarification"]),
            "auto_created": len(result["auto_created"]),
            "recommendations": []
        }
        
        # Add recommendations
        if result["potential_duplicates"]:
            result["summary"]["recommendations"].append(
                f"Review {len(result['potential_duplicates'])} potential duplicates before creating tasks"
            )
        
        if result["needs_clarification"]:
            result["summary"]["recommendations"].append(
                f"Clarify {len(result['needs_clarification'])} ambiguous items for better task definition"
            )
        
        if result["new_tasks"] and not auto_create:
            result["summary"]["recommendations"].append(
                f"Ready to create {len(result['new_tasks'])} new tasks - use auto_create=true or create manually"
            )
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "daily_checkin":
        task_updates = arguments.get('task_updates', [])
        
        if not task_updates:
            # Return active tasks for check-in prompting
            active_tasks = [t for t in get_all_tasks() if t.get('status') in ['s', 'n']]
            result = {
                "action": "prompt_for_checkin",
                "active_tasks": [
                    {
                        "title": task.get('title'),
                        "filename": task.get('filename'),
                        "status": task.get('status'),
                        "category": task.get('category')
                    }
                    for task in active_tasks
                ],
                "message": "Ready to start check-in process"
            }
        else:
            # Process the updates
            updated_tasks = []
            
            for update in task_updates:
                task_file = update['task_file']
                if not task_file.endswith('.md'):
                    task_file += '.md'
                
                filepath = TASKS_DIR / task_file
                if not filepath.exists():
                    continue
                
                # Read current task
                with open(filepath, 'r') as f:
                    content = f.read()
                metadata, body = parse_yaml_frontmatter(content)
                
                # Save time tracking data if work was done
                if update.get('worked_on') and update.get('time_spent'):
                    category = metadata.get('category', 'other')
                    work_completed = update.get('work_completed', 'Made progress')
                    time_spent = update.get('time_spent')
                    
                    # Estimate completion percentage
                    completion_pct = 1.0 if update.get('completed') else 0.3  # Default partial completion
                    
                    save_time_entry(category, work_completed, time_spent, completion_pct)
                
                # Save distraction data if present
                if update.get('had_distractions') and update.get('distractions'):
                    category = metadata.get('category', 'other')
                    task_title = metadata.get('title', '')
                    distractions = update.get('distractions')
                    distraction_time = update.get('distraction_time', 0)
                    
                    save_distraction_entry(category, distractions, distraction_time, task_title)
                
                # Update status if completed
                if update.get('completed'):
                    metadata['status'] = 'd'
                elif update.get('worked_on') and metadata.get('status') == 'n':
                    metadata['status'] = 's'
                
                # Add progress log entry
                progress_entry = f"\n## Progress Log\n- {datetime.now().strftime('%Y-%m-%d')}: "
                
                if update.get('completed'):
                    progress_entry += "Task completed"
                elif update.get('worked_on'):
                    work_done = update.get('work_completed', 'Made progress')
                    time_spent = update.get('time_spent', 0)
                    progress_entry += f"{work_done}"
                    if time_spent:
                        progress_entry += f" ({time_spent} min)"
                    
                    next_step = update.get('next_step')
                    if next_step:
                        progress_entry += f"\n  - Next: {next_step}"
                
                # Update the file
                if "## Progress Log" not in body:
                    body += progress_entry
                else:
                    # Add to existing progress log
                    body = body.replace("## Progress Log", progress_entry.replace("## Progress Log", "## Progress Log"))
                
                yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{yaml_str}---\n{body}"
                
                with open(filepath, 'w') as f:
                    f.write(new_content)
                
                updated_tasks.append({
                    "task": metadata.get('title'),
                    "filename": task_file,
                    "status": metadata.get('status'),
                    "completed": update.get('completed', False),
                    "worked_on": update.get('worked_on', False)
                })
            
            result = {
                "action": "checkin_complete",
                "updated_tasks": updated_tasks,
                "message": f"Check-in complete. Updated {len(updated_tasks)} tasks."
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_time_estimates":
        category = arguments.get('category')
        task_description = arguments.get('task_description', '')
        
        analytics = get_time_analytics(category=category)
        
        if not analytics['stats']:
            result = {
                "estimated_time": 60,  # Default fallback
                "confidence": "low",
                "reason": "No historical data available",
                "suggestion": "Start with 60 minutes and adjust based on actual time"
            }
        else:
            avg_time = analytics['stats'].get('avg_time', 60)
            count = analytics['stats'].get('total_entries', 0)
            
            # Adjust based on task complexity keywords
            complexity_multiplier = 1.0
            if any(word in task_description.lower() for word in ['complex', 'research', 'investigate', 'analyze']):
                complexity_multiplier = 1.5
            elif any(word in task_description.lower() for word in ['quick', 'simple', 'update', 'fix']):
                complexity_multiplier = 0.7
            
            estimated_time = int(avg_time * complexity_multiplier)
            confidence = "high" if count >= 5 else "medium" if count >= 2 else "low"
            
            result = {
                "estimated_time": estimated_time,
                "confidence": confidence,
                "historical_avg": int(avg_time),
                "data_points": count,
                "category": category,
                "complexity_adjustment": complexity_multiplier
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "view_time_analytics":
        category = arguments.get('category')
        days = arguments.get('days', 30)
        
        analytics = get_time_analytics(category=category, days=days)
        
        result = {
            "period_days": days,
            "category_filter": category,
            "total_entries": len(analytics['entries']),
            "stats": analytics['stats'],
            "recent_entries": analytics['entries'][-10:] if analytics['entries'] else []
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "view_distraction_analytics":
        days = arguments.get('days', 30)
        
        analytics = get_distraction_analytics(days=days)
        
        result = {
            "period_days": days,
            "total_distraction_entries": len(analytics['entries']),
            "stats": analytics['stats'],
            "insights": [],
            "recent_entries": analytics['entries'][-10:] if analytics['entries'] else []
        }
        
        # Add insights based on patterns
        if analytics['stats']:
            stats = analytics['stats']
            
            # Time-based insights
            if 'by_hour' in stats:
                peak_hour = max(stats['by_hour'], key=stats['by_hour'].get)
                result['insights'].append(f"Most distractions occur at {peak_hour}:00")
            
            # Day-based insights  
            if 'by_day_of_week' in stats:
                peak_day = max(stats['by_day_of_week'], key=stats['by_day_of_week'].get)
                result['insights'].append(f"Most distractions happen on {peak_day}")
            
            # Category insights
            if 'by_task_category' in stats:
                worst_category = max(stats['by_task_category'], key=stats['by_task_category'].get)
                result['insights'].append(f"Most distractions during {worst_category} tasks")
            
            # Common distractions
            if 'common_distractions' in stats and stats['common_distractions']:
                top_distraction = stats['common_distractions'][0][0]
                result['insights'].append(f"Top distraction: {top_distraction}")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_backlog_smart":
        auto_save_notes = arguments.get('auto_save_notes', False)
        auto_create_tasks = arguments.get('auto_create_tasks', False)
        
        # Read backlog
        backlog_file = BASE_DIR / 'BACKLOG.md'
        if not backlog_file.exists():
            return [types.TextContent(type="text", text=json.dumps({
                "error": "BACKLOG.md not found"
            }, indent=2))]
        
        with open(backlog_file, 'r') as f:
            content = f.read().strip()
        
        if not content or content == 'all done!':
            return [types.TextContent(type="text", text=json.dumps({
                "message": "Backlog is already clear"
            }, indent=2))]
        
        # Classify content
        classified = classify_backlog_content(content)
        
        result = {
            "classification": classified,
            "actions_taken": [],
            "recommendations": []
        }
        
        # Auto-save notes to Knowledge/
        if auto_save_notes and (classified['notes'] or classified['meeting_notes']):
            knowledge_dir = BASE_DIR / 'Knowledge'
            knowledge_dir.mkdir(exist_ok=True)
            
            for note in classified['notes'] + classified['meeting_notes']:
                filename = suggest_knowledge_filename(note['content'])
                filepath = knowledge_dir / filename
                
                # Add timestamp and save
                timestamped_content = f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n"
                timestamped_content += f"*Captured: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
                timestamped_content += note['content']
                
                with open(filepath, 'w') as f:
                    f.write(timestamped_content)
                
                result["actions_taken"].append(f"Saved note to {filepath}")
        
        # Auto-create tasks
        if auto_create_tasks and classified['tasks']:
            for task_item in classified['tasks']:
                task_content = task_item['content'].strip('- ')
                category = task_item['suggested_category']
                
                # Create task file
                filename = task_content.replace('/', '_').replace('\\', '_') + '.md'
                filepath = TASKS_DIR / filename
                
                metadata = {
                    'title': task_content,
                    'category': category,
                    'priority': 'P2',
                    'status': 'n',
                    'estimated_time': 30
                }
                
                yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
                file_content = f"---\n{yaml_str}---\n\n# {task_content}\n\nTask created from backlog processing."
                
                with open(filepath, 'w') as f:
                    f.write(file_content)
                
                result["actions_taken"].append(f"Created task: {task_content}")
        
        # Add recommendations
        if classified['notes'] and not auto_save_notes:
            result["recommendations"].append(f"Found {len(classified['notes'])} note sections - consider saving to Knowledge/")
        
        if classified['meeting_notes'] and not auto_save_notes:
            result["recommendations"].append(f"Found {len(classified['meeting_notes'])} meeting note sections - consider saving to Knowledge/")
        
        if classified['tasks'] and not auto_create_tasks:
            result["recommendations"].append(f"Found {len(classified['tasks'])} potential tasks - consider creating them")
        
        if classified['reminders']:
            result["recommendations"].append(f"Found {len(classified['reminders'])} reminders - consider scheduling or adding to calendar")
        
        if classified['ideas']:
            result["recommendations"].append(f"Found {len(classified['ideas'])} ideas - consider saving to Knowledge/ideas.md")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_session":
        current_task = arguments.get('current_task')
        status = arguments.get('status')
        notes = arguments.get('notes')
        next_action = arguments.get('next_action')
        
        success = update_session_tracker(current_task, status, notes, next_action)
        
        result = {
            "success": success,
            "updated": {
                "current_task": current_task,
                "status": status,
                "notes": notes,
                "next_action": next_action,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_session_status":
        session_data = get_session_tracker()
        
        # Add recommendations based on session state
        if session_data.get('session_active'):
            session_data['recommendations'] = [
                f"Resume working on: {session_data.get('current_task', 'Unknown task')}",
                f"Status: {session_data.get('status', 'Unknown')}",
                f"Next action: {session_data.get('next_action', 'Not specified')}"
            ]
        else:
            session_data['recommendations'] = [
                "No active session - ready to start fresh",
                "Check priority tasks to begin work"
            ]
        
        return [types.TextContent(type="text", text=json.dumps(session_data, indent=2))]
    
    elif name == "end_session":
        summary = arguments.get('summary', '')
        completed_tasks = arguments.get('completed_tasks', [])
        next_session_plan = arguments.get('next_session_plan', '')
        
        # Update session tracker to ended state
        update_session_tracker(
            current_task=None,
            status='ended',
            notes=f"Session ended. Summary: {summary}",
            next_action=next_session_plan
        )
        
        # Save session summary to knowledge
        session_summary = f"""# Session Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
{summary}

## Completed Tasks
{chr(10).join(f'- {task}' for task in completed_tasks) if completed_tasks else '- None'}

## Next Session Plan
{next_session_plan}
"""
        
        knowledge_dir = BASE_DIR / 'Knowledge'
        knowledge_dir.mkdir(exist_ok=True)
        
        session_file = knowledge_dir / f"session-{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(session_file, 'w') as f:
            f.write(session_summary)
        
        result = {
            "session_ended": True,
            "summary_saved": str(session_file),
            "completed_tasks": completed_tasks,
            "next_session_plan": next_session_plan
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "prepare_parallel_backlog_processing":
        include_existing = arguments.get('include_existing_tasks', True) if arguments else True
        
        # Read backlog
        backlog_file = BASE_DIR / 'BACKLOG.md'
        if not backlog_file.exists():
            return [types.TextContent(type="text", text=json.dumps({
                "error": "BACKLOG.md not found"
            }, indent=2))]
        
        with open(backlog_file, 'r') as f:
            content = f.read().strip()
        
        if not content or content == 'all done!':
            return [types.TextContent(type="text", text=json.dumps({
                "message": "Backlog is already clear",
                "items": []
            }, indent=2))]
        
        # Parse backlog items
        lines = content.split('\n')
        items = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                items.append(stripped[2:])
            elif stripped and not stripped.startswith('#'):
                # Capture non-list items too
                items.append(stripped)
        
        # Get existing tasks for context
        existing_tasks = []
        if include_existing:
            all_tasks = get_all_tasks()
            existing_tasks = [
                {
                    "title": t.get('title', ''),
                    "category": t.get('category', ''),
                    "status": t.get('status', ''),
                    "priority": t.get('priority', '')
                }
                for t in all_tasks if t.get('status') != 'd'
            ]
        
        result = {
            "operation": "parallel_backlog_processing",
            "total_items": len(items),
            "items": items,
            "existing_tasks_count": len(existing_tasks),
            "existing_tasks": existing_tasks[:50],  # Limit to 50 for context size
            "delegate_instructions": {
                "task": "Analyze this backlog item for duplicate detection, categorization, and task creation",
                "check_for": [
                    "Similarity to existing tasks (flag if >60% similar)",
                    "Ambiguity (flag if too vague)",
                    "Appropriate category (technical, outreach, research, writing, admin, personal, other)",
                    "Suggested priority (P0-P3)",
                    "Estimated time in minutes"
                ],
                "output_format": {
                    "item": "original item text",
                    "is_duplicate": "boolean",
                    "similar_to": "list of similar task titles",
                    "is_ambiguous": "boolean",
                    "clarification_needed": "list of questions if ambiguous",
                    "suggested_category": "category",
                    "suggested_priority": "P0-P3",
                    "estimated_time": "minutes",
                    "ready_to_create": "boolean"
                }
            }
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "prepare_parallel_task_analysis":
        analysis_types = arguments.get('analysis_types', ['priority', 'category', 'blockers']) if arguments else ['priority', 'category', 'blockers']
        
        all_tasks = get_all_tasks()
        active_tasks = [t for t in all_tasks if t.get('status') != 'd']
        
        # Read goals for context
        goals_content = ""
        goals_file = BASE_DIR / 'GOALS.md'
        if goals_file.exists():
            with open(goals_file, 'r') as f:
                goals_content = f.read()
        
        result = {
            "operation": "parallel_task_analysis",
            "total_active_tasks": len(active_tasks),
            "analysis_types": analysis_types,
            "delegates": []
        }
        
        # Create delegate configurations for each analysis type
        if 'priority' in analysis_types:
            result["delegates"].append({
                "identifier": "priority_analysis",
                "task": "Analyze priority distribution and balance",
                "data": {
                    "tasks_by_priority": {
                        "P0": [t for t in active_tasks if t.get('priority') == 'P0'],
                        "P1": [t for t in active_tasks if t.get('priority') == 'P1'],
                        "P2": [t for t in active_tasks if t.get('priority') == 'P2'],
                        "P3": [t for t in active_tasks if t.get('priority') == 'P3']
                    },
                    "limits": {"P0": 3, "P1": 7}
                },
                "output": "Priority balance assessment, overload warnings, recommendations"
            })
        
        if 'category' in analysis_types:
            by_category = {}
            for task in active_tasks:
                cat = task.get('category', 'other')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(task)
            
            result["delegates"].append({
                "identifier": "category_analysis",
                "task": "Analyze work distribution by category",
                "data": {"tasks_by_category": by_category},
                "output": "Category distribution, time estimates by category, balance recommendations"
            })
        
        if 'blockers' in analysis_types:
            blocked_tasks = [t for t in active_tasks if t.get('status') == 'b']
            started_tasks = [t for t in active_tasks if t.get('status') == 's']
            
            result["delegates"].append({
                "identifier": "blocker_analysis",
                "task": "Identify blockers and suggest unblocking actions",
                "data": {
                    "blocked_tasks": blocked_tasks,
                    "started_tasks": started_tasks
                },
                "output": "Blocker summary, suggested actions to unblock, task dependencies"
            })
        
        if 'goal_alignment' in analysis_types:
            result["delegates"].append({
                "identifier": "goal_alignment_analysis",
                "task": "Assess how tasks align with stated goals",
                "data": {
                    "tasks": active_tasks,
                    "goals": goals_content[:2000]  # Limit size
                },
                "output": "Goal alignment score, tasks not supporting goals, recommendations"
            })
        
        if 'time_estimates' in analysis_types:
            result["delegates"].append({
                "identifier": "time_analysis",
                "task": "Analyze time estimates and workload",
                "data": {
                    "tasks": active_tasks,
                    "total_estimated_time": sum(t.get('estimated_time', 30) for t in active_tasks)
                },
                "output": "Total workload hours, realistic completion timeline, overcommitment warnings"
            })
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "prepare_parallel_daily_planning":
        include_goals = arguments.get('include_goals', True) if arguments else True
        include_knowledge = arguments.get('include_knowledge', False) if arguments else False
        
        all_tasks = get_all_tasks()
        active_tasks = [t for t in all_tasks if t.get('status') != 'd']
        
        # Get high priority tasks
        p0_tasks = [t for t in active_tasks if t.get('priority') == 'P0']
        p1_tasks = [t for t in active_tasks if t.get('priority') == 'P1']
        started_tasks = [t for t in active_tasks if t.get('status') == 's']
        
        # Read goals
        goals_content = ""
        if include_goals:
            goals_file = BASE_DIR / 'GOALS.md'
            if goals_file.exists():
                with open(goals_file, 'r') as f:
                    goals_content = f.read()
        
        # Get recent knowledge files
        knowledge_files = []
        if include_knowledge:
            knowledge_dir = BASE_DIR / 'Knowledge'
            if knowledge_dir.exists():
                for kfile in sorted(knowledge_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                    knowledge_files.append({
                        "filename": kfile.name,
                        "modified": datetime.fromtimestamp(kfile.stat().st_mtime).isoformat()
                    })
        
        # Get current time context
        now = datetime.now()
        time_context = {
            "day": now.strftime('%A'),
            "date": now.strftime('%Y-%m-%d'),
            "hour": now.hour,
            "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"
        }
        
        result = {
            "operation": "parallel_daily_planning",
            "time_context": time_context,
            "delegates": [
                {
                    "identifier": "priority_focus",
                    "task": "Recommend top priority tasks for today",
                    "data": {
                        "p0_tasks": p0_tasks,
                        "p1_tasks": p1_tasks,
                        "time_available": "8 hours typical workday"
                    },
                    "output": "Top 3 tasks to focus on today with reasoning"
                },
                {
                    "identifier": "momentum_tasks",
                    "task": "Identify tasks with existing momentum",
                    "data": {
                        "started_tasks": started_tasks,
                        "time_context": time_context
                    },
                    "output": "Tasks to continue, quick wins, momentum opportunities"
                },
                {
                    "identifier": "goal_progress",
                    "task": "Suggest tasks that advance key goals",
                    "data": {
                        "goals": goals_content[:2000] if goals_content else "No goals defined",
                        "active_tasks": active_tasks[:30]
                    },
                    "output": "Goal-aligned task recommendations"
                }
            ],
            "knowledge_context": knowledge_files if include_knowledge else []
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "aggregate_parallel_results":
        operation_type = arguments.get('operation_type')
        delegate_results = arguments.get('delegate_results', [])
        auto_create = arguments.get('auto_create_tasks', False)
        
        if not operation_type or not delegate_results:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "Missing operation_type or delegate_results"
            }, indent=2))]
        
        result = {
            "operation": operation_type,
            "delegates_processed": len(delegate_results),
            "summary": {},
            "actions_taken": [],
            "recommendations": []
        }
        
        if operation_type == "backlog_processing":
            # Aggregate backlog processing results
            ready_to_create = []
            duplicates = []
            needs_clarification = []
            
            for delegate_result in delegate_results:
                if delegate_result.get('ready_to_create'):
                    ready_to_create.append(delegate_result)
                elif delegate_result.get('is_duplicate'):
                    duplicates.append(delegate_result)
                elif delegate_result.get('is_ambiguous'):
                    needs_clarification.append(delegate_result)
            
            result["summary"] = {
                "ready_to_create": len(ready_to_create),
                "duplicates": len(duplicates),
                "needs_clarification": len(needs_clarification)
            }
            
            # Auto-create tasks if requested
            if auto_create and ready_to_create:
                for item_data in ready_to_create:
                    title = item_data.get('item', '')
                    category = item_data.get('suggested_category', 'other')
                    priority = item_data.get('suggested_priority', 'P2')
                    estimated_time = item_data.get('estimated_time', 60)
                    
                    # Create task file
                    safe_filename = re.sub(r'[^\w\s-]', '', title)
                    safe_filename = re.sub(r'[-\s]+', ' ', safe_filename).strip()
                    filepath = TASKS_DIR / f"{safe_filename}.md"
                    
                    metadata = {
                        'title': title,
                        'category': category,
                        'priority': priority,
                        'status': 'n',
                        'estimated_time': estimated_time,
                        'created_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
                    task_content = generate_task_content(title, category)
                    file_content = f"---\n{yaml_str}---\n\n# {title}\n\n{task_content}"
                    
                    with open(filepath, 'w') as f:
                        f.write(file_content)
                    
                    result["actions_taken"].append(f"Created task: {title}")
            
            result["duplicates"] = duplicates
            result["needs_clarification"] = needs_clarification
            result["ready_to_create"] = ready_to_create if not auto_create else []
            
        elif operation_type == "task_analysis":
            # Aggregate analysis results
            result["analysis_results"] = delegate_results
            result["summary"] = {
                "analyses_completed": len(delegate_results),
                "analysis_types": [r.get('identifier', 'unknown') for r in delegate_results]
            }
            
        elif operation_type == "daily_planning":
            # Aggregate planning recommendations
            all_recommendations = []
            for delegate_result in delegate_results:
                if 'recommendations' in delegate_result:
                    all_recommendations.extend(delegate_result['recommendations'])
            
            result["recommendations"] = all_recommendations
            result["planning_results"] = delegate_results
            result["summary"] = {
                "total_recommendations": len(all_recommendations),
                "delegates_consulted": len(delegate_results)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # Knowledge Management Tools
    elif name == "create_knowledge":
        title = arguments['title']
        content = arguments['content']
        links = arguments.get('links', [])
        tags = arguments.get('tags', [])
        related_people = arguments.get('related_people', [])
        
        try:
            doc_path = knowledge_manager.create_knowledge(
                title=title,
                content=content,
                links=links,
                tags=tags,
                related_people=related_people
            )
            
            result = {
                "success": True,
                "doc_id": doc_path.stem,
                "path": str(doc_path),
                "message": f"Knowledge document '{title}' created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating knowledge document: {e}")
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
            
            if success:
                result = {
                    "success": True,
                    "doc_id": doc_id,
                    "message": f"Knowledge document '{doc_id}' updated successfully"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Failed to update document '{doc_id}'"
                }
        except Exception as e:
            logger.error(f"Error updating knowledge document: {e}")
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
                "count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_related_knowledge":
        doc_id = arguments['doc_id']
        depth = arguments.get('depth', 1)
        
        try:
            related = knowledge_manager.get_related_knowledge(doc_id, depth)
            
            # Also get backlinks
            backlinks = knowledge_manager.get_backlinks(doc_id)
            
            result = {
                "success": True,
                "doc_id": doc_id,
                "depth": depth,
                "related_count": len(related),
                "related_documents": related,
                "backlinks_count": len(backlinks),
                "backlinks": backlinks
            }
        except Exception as e:
            logger.error(f"Error getting related knowledge: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "validate_wikilinks":
        doc_id = arguments.get('doc_id') if arguments else None
        
        try:
            if doc_id:
                # Validate single document
                doc_path = wikilink_resolver.resolve_link(doc_id)
                if not doc_path or not doc_path.exists():
                    result = {
                        "success": False,
                        "error": f"Document not found: {doc_id}"
                    }
                else:
                    broken_links = wikilink_resolver.validate_links(doc_path)
                    result = {
                        "success": True,
                        "doc_id": doc_id,
                        "path": str(doc_path),
                        "broken_links_count": len(broken_links),
                        "broken_links": broken_links
                    }
            else:
                # Validate all documents in Knowledge directory
                knowledge_dir = BASE_DIR / 'Knowledge'
                all_broken = []
                
                for doc_path in knowledge_dir.glob('*.md'):
                    broken_links = wikilink_resolver.validate_links(doc_path)
                    if broken_links:
                        all_broken.append({
                            "doc_id": doc_path.stem,
                            "path": str(doc_path),
                            "broken_links": broken_links
                        })
                
                result = {
                    "success": True,
                    "documents_checked": len(list(knowledge_dir.glob('*.md'))),
                    "documents_with_broken_links": len(all_broken),
                    "broken_links": all_broken
                }
        except Exception as e:
            logger.error(f"Error validating wikilinks: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # People Management Tools
    elif name == "create_person":
        person_name = arguments['name']
        metadata = arguments.get('metadata')
        
        try:
            person_path = people_manager.create_person(person_name, metadata)
            
            result = {
                "success": True,
                "person_id": person_path.stem,
                "path": str(person_path),
                "message": f"Person profile '{person_name}' created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating person profile: {e}")
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
            
            if success:
                result = {
                    "success": True,
                    "person_id": person_id,
                    "message": f"Person profile '{person_id}' updated successfully"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Failed to update person profile '{person_id}'"
                }
        except Exception as e:
            logger.error(f"Error updating person profile: {e}")
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
            success = people_manager.link_to_knowledge(person_id, knowledge_id, context)
            
            if success:
                result = {
                    "success": True,
                    "person_id": person_id,
                    "knowledge_id": knowledge_id,
                    "message": f"Linked '{person_id}' to '{knowledge_id}' successfully"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Failed to link '{person_id}' to '{knowledge_id}'"
                }
        except Exception as e:
            logger.error(f"Error linking person to knowledge: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "link_people":
        person1_id = arguments['person1_id']
        person2_id = arguments['person2_id']
        relationship = arguments['relationship']
        context = arguments.get('context', '')
        
        try:
            success = people_manager.link_people(person1_id, person2_id, relationship, context)
            
            if success:
                result = {
                    "success": True,
                    "person1_id": person1_id,
                    "person2_id": person2_id,
                    "relationship": relationship,
                    "message": f"Linked '{person1_id}' to '{person2_id}' with relationship '{relationship}'"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Failed to link '{person1_id}' to '{person2_id}'"
                }
        except Exception as e:
            logger.error(f"Error linking people: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "find_expertise":
        topic = arguments['topic']
        
        try:
            experts = people_manager.find_expertise(topic)
            
            result = {
                "success": True,
                "topic": topic,
                "count": len(experts),
                "experts": experts
            }
        except Exception as e:
            logger.error(f"Error finding expertise: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # Time Tracking Tools
    elif name == "start_work":
        description = arguments['description']
        work_type = arguments.get('work_type', 'general')
        knowledge_refs = arguments.get('knowledge_refs', [])
        people_refs = arguments.get('people_refs', [])
        
        try:
            work_id = time_intelligence.start_work(
                description=description,
                work_type=work_type,
                knowledge_refs=knowledge_refs,
                people_refs=people_refs
            )
            
            result = {
                "success": True,
                "work_id": work_id,
                "description": description,
                "work_type": work_type,
                "knowledge_refs": knowledge_refs,
                "people_refs": people_refs,
                "message": f"Started tracking work: {description}"
            }
        except Exception as e:
            logger.error(f"Error starting work: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "end_work":
        work_id = arguments['work_id']
        completion_notes = arguments.get('completion_notes', '')
        completion_percentage = arguments.get('completion_percentage')
        
        try:
            time_entry = time_intelligence.end_work(
                work_id=work_id,
                completion_notes=completion_notes,
                completion_percentage=completion_percentage
            )
            
            if time_entry:
                result = {
                    "success": True,
                    "work_id": work_id,
                    "duration_minutes": time_entry.duration_minutes,
                    "work_description": time_entry.work_description,
                    "work_type": time_entry.work_type,
                    "start_time": time_entry.start_time,
                    "end_time": time_entry.end_time,
                    "completion_percentage": time_entry.completion_percentage,
                    "notes": time_entry.notes,
                    "message": f"Completed work tracking: {time_entry.duration_minutes} minutes"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Work entry not found: {work_id}"
                }
        except Exception as e:
            logger.error(f"Error ending work: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "record_distraction":
        work_id = arguments['work_id']
        distraction_type = arguments['distraction_type']
        duration_minutes = arguments['duration_minutes']
        description = arguments.get('description', '')
        
        try:
            success = time_intelligence.record_distraction(
                work_id=work_id,
                distraction_type=distraction_type,
                duration_minutes=duration_minutes,
                description=description
            )
            
            if success:
                result = {
                    "success": True,
                    "work_id": work_id,
                    "distraction_type": distraction_type,
                    "duration_minutes": duration_minutes,
                    "message": f"Recorded {distraction_type} distraction: {duration_minutes} minutes"
                }
            else:
                result = {
                    "success": False,
                    "error": f"Work entry not found: {work_id}"
                }
        except Exception as e:
            logger.error(f"Error recording distraction: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_time_history":
        work_type = arguments.get('work_type')
        knowledge_ref = arguments.get('knowledge_ref')
        person_ref = arguments.get('person_ref')
        days = arguments.get('days', 30)
        
        try:
            # Get entries based on filters
            if knowledge_ref:
                entries = time_intelligence.get_entries_by_knowledge(knowledge_ref)
            elif person_ref:
                entries = time_intelligence.get_entries_by_person(person_ref)
            elif work_type:
                entries = time_intelligence.get_entries_by_work_type(work_type)
            else:
                entries = time_intelligence.get_all_entries()
            
            # Filter by date if days specified
            if days:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                entries = [
                    e for e in entries
                    if e.start_time and datetime.fromisoformat(e.start_time) >= cutoff_date
                ]
            
            # Convert to dict for JSON serialization
            entries_data = [
                {
                    "id": e.id,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "duration_minutes": e.duration_minutes,
                    "work_description": e.work_description,
                    "work_type": e.work_type,
                    "knowledge_refs": e.knowledge_refs,
                    "people_refs": e.people_refs,
                    "distractions": e.distractions,
                    "completion_percentage": e.completion_percentage,
                    "notes": e.notes
                }
                for e in entries
            ]
            
            # Calculate summary statistics
            completed_entries = [e for e in entries if e.duration_minutes is not None]
            total_minutes = sum(e.duration_minutes for e in completed_entries)
            
            result = {
                "success": True,
                "count": len(entries),
                "completed_count": len(completed_entries),
                "total_minutes": total_minutes,
                "total_hours": round(total_minutes / 60, 1),
                "filters": {
                    "work_type": work_type,
                    "knowledge_ref": knowledge_ref,
                    "person_ref": person_ref,
                    "days": days
                },
                "entries": entries_data
            }
        except Exception as e:
            logger.error(f"Error getting time history: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_time_estimate":
        work_description = arguments['work_description']
        work_type = arguments['work_type']
        knowledge_refs = arguments.get('knowledge_refs', [])
        people_refs = arguments.get('people_refs', [])
        include_distraction_overhead = arguments.get('include_distraction_overhead', False)
        adjust_for_experience = arguments.get('adjust_for_experience', False)
        adjust_for_collaboration = arguments.get('adjust_for_collaboration', False)
        
        try:
            # Choose the appropriate estimation method based on flags
            if adjust_for_collaboration and people_refs:
                estimate = time_intelligence.generate_collaboration_adjusted_estimate(
                    work_description=work_description,
                    work_type=work_type,
                    people_refs=people_refs,
                    knowledge_refs=knowledge_refs
                )
            elif adjust_for_experience and knowledge_refs:
                estimate = time_intelligence.generate_experience_adjusted_estimate(
                    work_description=work_description,
                    work_type=work_type,
                    knowledge_refs=knowledge_refs
                )
            elif include_distraction_overhead:
                estimate = time_intelligence.generate_estimate_with_distraction_overhead(
                    work_description=work_description,
                    work_type=work_type,
                    knowledge_refs=knowledge_refs
                )
            else:
                estimate = time_intelligence.generate_estimate(
                    work_description=work_description,
                    work_type=work_type,
                    knowledge_refs=knowledge_refs
                )
            
            if estimate:
                result = {
                    "success": True,
                    "work_description": work_description,
                    "work_type": work_type,
                    "estimate": {
                        "mean_minutes": estimate.mean_minutes,
                        "mean_hours": round(estimate.mean_minutes / 60, 1),
                        "min_estimate": estimate.min_estimate,
                        "max_estimate": estimate.max_estimate,
                        "confidence_range_minutes": estimate.confidence_range,
                        "confidence_range_hours": (
                            round(estimate.confidence_range[0] / 60, 1),
                            round(estimate.confidence_range[1] / 60, 1)
                        ),
                        "variance": estimate.variance,
                        "std_dev": estimate.std_dev,
                        "similar_work_count": estimate.similar_work_count,
                        "similar_work_ids": estimate.similar_work_ids,
                        "explanation": estimate.explanation
                    },
                    "adjustments_applied": {
                        "distraction_overhead": include_distraction_overhead,
                        "experience_level": adjust_for_experience,
                        "collaboration_history": adjust_for_collaboration
                    }
                }
            else:
                result = {
                    "success": False,
                    "error": "No similar work found to generate estimate",
                    "work_description": work_description,
                    "work_type": work_type,
                    "suggestion": "Try a different work type or add more historical data"
                }
        except Exception as e:
            logger.error(f"Error generating estimate: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "suggest_work_breakdown":
        work_description = arguments['work_description']
        work_type = arguments['work_type']
        knowledge_refs = arguments.get('knowledge_refs', [])
        accept_breakdown = arguments.get('accept_breakdown', False)
        
        try:
            breakdown = time_intelligence.suggest_breakdown(
                work_description=work_description,
                work_type=work_type,
                knowledge_refs=knowledge_refs
            )
            
            if breakdown:
                # Convert chunks to dict for JSON serialization
                chunks_data = [
                    {
                        "id": chunk.id,
                        "description": chunk.description,
                        "estimated_minutes": chunk.estimated_minutes,
                        "estimated_hours": round(chunk.estimated_minutes / 60, 1),
                        "work_type": chunk.work_type,
                        "knowledge_refs": chunk.knowledge_refs,
                        "dependencies": chunk.dependencies
                    }
                    for chunk in breakdown.chunks
                ]
                
                result = {
                    "success": True,
                    "original_work": breakdown.original_work,
                    "breakdown_id": breakdown.breakdown_id,
                    "total_chunks": len(breakdown.chunks),
                    "estimated_total_minutes": breakdown.estimated_total,
                    "estimated_total_hours": round(breakdown.estimated_total / 60, 1),
                    "chunks": chunks_data,
                    "created_at": breakdown.created_at
                }
                
                # If accept_breakdown is True, create time entries for each chunk
                if accept_breakdown:
                    work_ids = time_intelligence.accept_breakdown(breakdown)
                    result["accepted"] = True
                    result["work_ids"] = work_ids
                    result["message"] = f"Breakdown accepted. Created {len(work_ids)} time tracking entries."
                else:
                    result["accepted"] = False
                    result["message"] = "Breakdown suggested. Set 'accept_breakdown' to true to create time entries."
            else:
                result = {
                    "success": False,
                    "error": "Work complexity is too low to suggest breakdown",
                    "work_description": work_description,
                    "suggestion": "This work item appears simple enough to track as a single entry"
                }
        except Exception as e:
            logger.error(f"Error suggesting work breakdown: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_notes_inbox":
        notes_file = arguments.get('notes_file')
        notes_file_path = Path(notes_file) if notes_file else None
        
        try:
            # Process notes in batch mode
            processing_result = notes_processor.process_batch(notes_file_path)
            
            # Apply updates using knowledge_manager and people_manager
            applied_updates = {
                "knowledge_created": [],
                "knowledge_updated": [],
                "people_created": [],
                "people_updated": [],
                "errors": []
            }
            
            # Create/update knowledge documents
            for title in processing_result.knowledge_created:
                try:
                    # Find the note content for this knowledge topic
                    # For now, create a basic document
                    doc_path = knowledge_manager.create_knowledge(
                        title=title,
                        content=f"# {title}\n\nCreated from notes inbox processing.",
                        tags=[],
                        links=[]
                    )
                    applied_updates["knowledge_created"].append(str(doc_path))
                except Exception as e:
                    logger.error(f"Error creating knowledge '{title}': {e}")
                    applied_updates["errors"].append(f"Failed to create knowledge '{title}': {str(e)}")
            
            for title in processing_result.knowledge_updated:
                try:
                    # Update existing knowledge document
                    success = knowledge_manager.update_knowledge(
                        doc_id=title,
                        additional_content=f"\n\nUpdated from notes inbox processing on {datetime.now().strftime('%Y-%m-%d')}."
                    )
                    if success:
                        applied_updates["knowledge_updated"].append(title)
                except Exception as e:
                    logger.error(f"Error updating knowledge '{title}': {e}")
                    applied_updates["errors"].append(f"Failed to update knowledge '{title}': {str(e)}")
            
            # Create/update person profiles
            for name in processing_result.people_created:
                try:
                    person_path = people_manager.create_person(
                        name=name,
                        role="",
                        team="",
                        metadata={}
                    )
                    applied_updates["people_created"].append(str(person_path))
                except Exception as e:
                    logger.error(f"Error creating person '{name}': {e}")
                    applied_updates["errors"].append(f"Failed to create person '{name}': {str(e)}")
            
            for name in processing_result.people_updated:
                try:
                    success = people_manager.update_person(
                        person_id=name,
                        additional_context=f"Mentioned in notes inbox on {datetime.now().strftime('%Y-%m-%d')}."
                    )
                    if success:
                        applied_updates["people_updated"].append(name)
                except Exception as e:
                    logger.error(f"Error updating person '{name}': {e}")
                    applied_updates["errors"].append(f"Failed to update person '{name}': {str(e)}")
            
            result = {
                "success": True,
                "processed_count": processing_result.processed_count,
                "summary": processing_result.summary,
                "applied_updates": applied_updates,
                "processing_errors": processing_result.errors
            }
        except Exception as e:
            logger.error(f"Error processing notes inbox: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_notes_interactive":
        notes_file = arguments.get('notes_file')
        notes_file_path = Path(notes_file) if notes_file else None
        
        try:
            # Start interactive session
            session = notes_processor.process_interactive(notes_file_path)
            
            # Store session in memory (in production, would use proper session storage)
            if not hasattr(notes_processor, '_sessions'):
                notes_processor._sessions = {}
            notes_processor._sessions[session.session_id] = session
            
            result = {
                "success": True,
                "session_id": session.session_id,
                "total_notes": len(session.notes),
                "current_index": session.current_index,
                "message": f"Interactive session started with {len(session.notes)} notes to process"
            }
        except Exception as e:
            logger.error(f"Error starting interactive session: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_interactive_note":
        session_id = arguments['session_id']
        clarifications = arguments.get('clarifications', {})
        confirmed = arguments.get('confirmed', False)
        advance = arguments.get('advance', False)
        
        try:
            # Retrieve session
            if not hasattr(notes_processor, '_sessions') or session_id not in notes_processor._sessions:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }, indent=2))]
            
            session = notes_processor._sessions[session_id]
            
            # If clarifications provided, incorporate them
            if clarifications and session.current_index < len(session.processed_notes):
                processed_note = notes_processor.incorporate_clarifications(
                    session, 
                    session.current_index, 
                    clarifications
                )
                
                result = {
                    "success": True,
                    "session_id": session_id,
                    "clarifications_incorporated": True,
                    "note_index": session.current_index,
                    "requires_confirmation": True,
                    "message": "Clarifications incorporated. Please confirm to apply updates."
                }
            
            # If confirmed, apply updates
            elif confirmed and session.current_index < len(session.processed_notes):
                update_result = notes_processor.confirm_updates(session, session.current_index, True)
                
                # Apply the updates using knowledge_manager and people_manager
                applied = []
                errors = []
                
                for update in update_result.get('updates', []):
                    try:
                        action = update.get('action')
                        if action == 'create_knowledge':
                            doc_path = knowledge_manager.create_knowledge(
                                title=update['title'],
                                content=update['content'],
                                tags=[],
                                links=[]
                            )
                            applied.append(f"Created knowledge: {update['title']}")
                        elif action == 'update_knowledge':
                            success = knowledge_manager.update_knowledge(
                                doc_id=update['title'],
                                additional_content=update['additional_content']
                            )
                            if success:
                                applied.append(f"Updated knowledge: {update['title']}")
                        elif action == 'create_person':
                            person_path = people_manager.create_person(
                                name=update['name'],
                                role="",
                                team="",
                                metadata={"context": update['context']}
                            )
                            applied.append(f"Created person: {update['name']}")
                        elif action == 'update_person':
                            success = people_manager.update_person(
                                person_id=update['name'],
                                additional_context=update['additional_context']
                            )
                            if success:
                                applied.append(f"Updated person: {update['name']}")
                    except Exception as e:
                        logger.error(f"Error applying update: {e}")
                        errors.append(f"Failed to apply {action}: {str(e)}")
                
                result = {
                    "success": True,
                    "session_id": session_id,
                    "updates_applied": True,
                    "note_index": session.current_index,
                    "applied_updates": applied,
                    "errors": errors
                }
            
            # If advance, move to next note
            elif advance:
                notes_processor.advance_session(session)
                
                # Process next note if available
                if session.current_index < len(session.notes):
                    processed_note = notes_processor.process_next_note(session)
                    
                    if processed_note:
                        result = {
                            "success": True,
                            "session_id": session_id,
                            "note_index": session.current_index,
                            "note_text": processed_note.original_text,
                            "note_type": processed_note.note_type,
                            "requires_clarification": processed_note.requires_clarification,
                            "clarification_questions": processed_note.clarification_questions,
                            "entities": [e.to_dict() for e in processed_note.entities],
                            "remaining_notes": len(session.notes) - session.current_index - 1
                        }
                    else:
                        result = {
                            "success": False,
                            "session_id": session_id,
                            "error": "Failed to process note"
                        }
                else:
                    result = {
                        "success": True,
                        "session_id": session_id,
                        "session_complete": True,
                        "message": "All notes processed"
                    }
            
            # Otherwise, just process current note
            else:
                processed_note = notes_processor.process_next_note(session)
                
                if processed_note:
                    result = {
                        "success": True,
                        "session_id": session_id,
                        "note_index": session.current_index,
                        "note_text": processed_note.original_text,
                        "note_type": processed_note.note_type,
                        "requires_clarification": processed_note.requires_clarification,
                        "clarification_questions": processed_note.clarification_questions,
                        "entities": [e.to_dict() for e in processed_note.entities],
                        "remaining_notes": len(session.notes) - session.current_index - 1
                    }
                else:
                    result = {
                        "success": True,
                        "session_id": session_id,
                        "session_complete": True,
                        "message": "All notes processed"
                    }
        
        except Exception as e:
            logger.error(f"Error processing interactive note: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_conversational_note":
        note_text = arguments['note_text']
        context = arguments.get('context')
        apply_updates = arguments.get('apply_updates', False)
        proposed_updates = arguments.get('proposed_updates', [])
        
        try:
            if apply_updates and proposed_updates:
                # Apply the proposed updates
                apply_result = notes_processor.apply_conversational_updates(proposed_updates, True)
                
                # Actually apply using knowledge_manager and people_manager
                applied = []
                errors = []
                
                for update in apply_result.get('updates', []):
                    try:
                        update_type = update.get('type')
                        if update_type == 'knowledge_created':
                            doc_path = knowledge_manager.create_knowledge(
                                title=update['title'],
                                content=update['content'],
                                tags=[],
                                links=[]
                            )
                            applied.append(f"Created knowledge: {update['title']}")
                        elif update_type == 'knowledge_updated':
                            success = knowledge_manager.update_knowledge(
                                doc_id=update['title'],
                                additional_content=update['additional_content']
                            )
                            if success:
                                applied.append(f"Updated knowledge: {update['title']}")
                        elif update_type == 'person_created':
                            person_path = people_manager.create_person(
                                name=update['name'],
                                role="",
                                team="",
                                metadata={"context": update['context']}
                            )
                            applied.append(f"Created person: {update['name']}")
                        elif update_type == 'person_updated':
                            success = people_manager.update_person(
                                person_id=update['name'],
                                additional_context=update['additional_context']
                            )
                            if success:
                                applied.append(f"Updated person: {update['name']}")
                    except Exception as e:
                        logger.error(f"Error applying update: {e}")
                        errors.append(f"Failed to apply {update_type}: {str(e)}")
                
                result = {
                    "success": True,
                    "updates_applied": True,
                    "applied_updates": applied,
                    "errors": errors,
                    "message": apply_result.get('message', '')
                }
            else:
                # Process the note and propose updates
                response = notes_processor.process_conversational(note_text, context)
                
                result = {
                    "success": True,
                    "entities_detected": [e.to_dict() for e in response.entities_detected],
                    "clarification_questions": response.clarification_questions,
                    "proposed_updates": response.proposed_updates,
                    "requires_confirmation": response.requires_confirmation
                }
        except Exception as e:
            logger.error(f"Error processing conversational note: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_meeting_notes":
        attendees = arguments['attendees']
        topics = arguments['topics']
        notes = arguments['notes']
        date = arguments.get('date', datetime.now().isoformat())
        
        try:
            # Process meeting notes
            meeting_data = {
                'attendees': attendees,
                'topics': topics,
                'notes': notes,
                'date': date
            }
            
            meeting_result = notes_processor.process_meeting_notes(meeting_data)
            
            # Apply updates using knowledge_manager and people_manager
            applied_updates = {
                "knowledge_created": [],
                "knowledge_updated": [],
                "people_updated": [],
                "connections_created": [],
                "errors": []
            }
            
            # Create/update knowledge documents for topics
            for topic in meeting_result.knowledge_created:
                try:
                    doc_path = knowledge_manager.create_knowledge(
                        title=topic,
                        content=f"# {topic}\n\nDiscussed in meeting {meeting_result.meeting_id}\n\n{notes}",
                        tags=["meeting"],
                        links=[]
                    )
                    applied_updates["knowledge_created"].append(str(doc_path))
                except Exception as e:
                    logger.error(f"Error creating knowledge '{topic}': {e}")
                    applied_updates["errors"].append(f"Failed to create knowledge '{topic}': {str(e)}")
            
            for topic in meeting_result.knowledge_updated:
                try:
                    success = knowledge_manager.update_knowledge(
                        doc_id=topic,
                        additional_content=f"\n\n## Meeting Notes - {date}\n\n{notes}"
                    )
                    if success:
                        applied_updates["knowledge_updated"].append(topic)
                except Exception as e:
                    logger.error(f"Error updating knowledge '{topic}': {e}")
                    applied_updates["errors"].append(f"Failed to update knowledge '{topic}': {str(e)}")
            
            # Update person profiles for attendees
            for attendee in meeting_result.people_updated:
                try:
                    success = people_manager.update_person(
                        person_id=attendee,
                        additional_context=f"Attended meeting on {date}. Topics: {', '.join(topics)}"
                    )
                    if success:
                        applied_updates["people_updated"].append(attendee)
                except Exception as e:
                    logger.error(f"Error updating person '{attendee}': {e}")
                    applied_updates["errors"].append(f"Failed to update person '{attendee}': {str(e)}")
            
            # Create connections
            for connection in meeting_result.connections_created:
                try:
                    if connection['type'] == 'person_to_knowledge':
                        success = people_manager.link_to_knowledge(
                            person_id=connection['source'],
                            knowledge_id=connection['target'],
                            context=connection['context']
                        )
                        if success:
                            applied_updates["connections_created"].append(
                                f"{connection['source']} -> {connection['target']}"
                            )
                except Exception as e:
                    logger.error(f"Error creating connection: {e}")
                    applied_updates["errors"].append(f"Failed to create connection: {str(e)}")
            
            result = {
                "success": True,
                "meeting_id": meeting_result.meeting_id,
                "summary": meeting_result.summary,
                "applied_updates": applied_updates
            }
        except Exception as e:
            logger.error(f"Error processing meeting notes: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # Analysis Tools
    elif name == "get_distraction_analysis":
        days = arguments.get('days')
        work_type = arguments.get('work_type')
        include_impact = arguments.get('include_impact', True)
        
        try:
            # Get distraction patterns
            patterns = time_intelligence.analyze_distraction_patterns(
                days=days,
                work_type=work_type
            )
            
            result = {
                "success": True,
                "patterns": patterns
            }
            
            # Add impact analysis if requested
            if include_impact:
                impact = time_intelligence.calculate_distraction_impact(work_type=work_type)
                result["impact"] = impact
            
            # Add filters info
            result["filters"] = {
                "days": days if days else "all time",
                "work_type": work_type if work_type else "all types"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing distractions: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_expertise_analysis":
        min_minutes = arguments.get('min_minutes', 60)
        
        try:
            # Get expertise ranking by time investment
            expertise_areas = time_intelligence.rank_expertise_by_time(min_minutes=min_minutes)
            
            result = {
                "success": True,
                "expertise_areas": expertise_areas,
                "total_areas": len(expertise_areas),
                "min_minutes_threshold": min_minutes
            }
            
            # Add summary statistics
            if expertise_areas:
                total_time = sum(area["total_minutes"] for area in expertise_areas)
                result["summary"] = {
                    "total_time_minutes": total_time,
                    "total_time_hours": round(total_time / 60, 1),
                    "top_expertise": expertise_areas[0]["knowledge_ref"] if expertise_areas else None,
                    "top_expertise_hours": round(expertise_areas[0]["total_minutes"] / 60, 1) if expertise_areas else 0
                }
            
        except Exception as e:
            logger.error(f"Error analyzing expertise: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_collaboration_analysis":
        days = arguments.get('days')
        
        try:
            # Get collaboration patterns
            patterns = time_intelligence.identify_collaboration_patterns(days=days)
            
            result = {
                "success": True,
                "patterns": patterns,
                "filters": {
                    "days": days if days else "all time"
                }
            }
            
            # Add summary insights
            if patterns["frequent_collaborators"]:
                top_collaborator = patterns["frequent_collaborators"][0]
                result["summary"] = {
                    "top_collaborator": top_collaborator["person_ref"],
                    "top_collaborator_hours": round(top_collaborator["total_minutes"] / 60, 1),
                    "collaboration_percentage": round(patterns["collaboration_percentage"], 1),
                    "total_collaborators": len(patterns["frequent_collaborators"])
                }
            
        except Exception as e:
            logger.error(f"Error analyzing collaboration: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_time_trends":
        knowledge_ref = arguments.get('knowledge_ref')
        days = arguments.get('days', 90)
        group_by = arguments.get('group_by', 'week')
        
        try:
            # Get time trends
            trends = time_intelligence.get_time_trends_by_knowledge(
                knowledge_ref=knowledge_ref,
                days=days,
                group_by=group_by
            )
            
            result = {
                "success": True,
                "trends": trends,
                "filters": {
                    "knowledge_ref": knowledge_ref if knowledge_ref else "all areas",
                    "days": days,
                    "group_by": group_by
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time trends: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main entry point for the MCP server"""
    logger.info(f"Starting Manager AI MCP Server")
    logger.info(f"Working directory: {BASE_DIR}")
    logger.info(f"Tasks directory: {TASKS_DIR}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="manager-ai-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())