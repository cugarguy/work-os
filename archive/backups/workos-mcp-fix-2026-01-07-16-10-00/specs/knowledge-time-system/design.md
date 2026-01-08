# Design Document: Knowledge and Time Intelligence System

## Overview

This design transforms WorkOS from a task management system into a knowledge and time intelligence system. The system will maintain a connected knowledge base using wikilinks, track people and their relationships, process raw notes into structured knowledge, and provide time estimation intelligence based on historical work patterns.

The system retains the existing MCP server architecture and markdown-based file structure while shifting focus from task prioritization to knowledge connectivity and time intelligence.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interactions                        │
│  (CLI Chat, File Dumps, Meeting Notes, Conversational)      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                    MCP Server Layer                          │
│  - Notes Processing Engine                                   │
│  - Knowledge Graph Manager                                   │
│  - People Network Manager                                    │
│  - Time Intelligence Engine                                  │
│  - Wikilink Parser & Resolver                               │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Storage Layer                              │
│  Knowledge/  People/  .system/  time_analytics.json         │
│  (Markdown files with YAML frontmatter + wikilinks)         │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Input Layer**: User provides notes via file (BACKLOG.md), conversation, or meeting notes
2. **Processing Layer**: MCP server analyzes content, extracts entities, asks clarifications
3. **Knowledge Layer**: Creates/updates knowledge documents with wikilinks
4. **People Layer**: Updates person profiles and relationship connections
5. **Time Layer**: Records work duration, analyzes patterns, provides estimates


## Components and Interfaces

### 1. Notes Processing Engine

**Purpose**: Process raw notes from multiple input sources and route to appropriate handlers.

**Interfaces**:
```python
class NotesProcessor:
    def process_batch(notes_file: Path) -> ProcessingResult
    def process_interactive(notes_file: Path) -> InteractiveSession
    def process_conversational(note_text: str) -> ConversationResponse
    def process_meeting_notes(meeting_data: dict) -> MeetingProcessingResult
```

**Responsibilities**:
- Read notes from file or conversation
- Identify note type (knowledge, people, time entry, meeting)
- Extract entities (topics, people mentions, time references)
- Route to appropriate specialized processor
- Handle ambiguity detection and clarification requests

### 2. Knowledge Graph Manager

**Purpose**: Manage knowledge documents and wikilink relationships.

**Interfaces**:
```python
class KnowledgeManager:
    def create_knowledge(title: str, content: str, links: List[str]) -> Path
    def update_knowledge(doc_id: str, updates: dict) -> bool
    def add_wikilink(source: str, target: str, context: str) -> bool
    def get_related_knowledge(doc_id: str, depth: int = 1) -> List[dict]
    def search_knowledge(query: str) -> List[dict]
    def get_backlinks(doc_id: str) -> List[dict]
```

**Responsibilities**:
- Create and update knowledge markdown files
- Parse and maintain wikilink relationships
- Provide graph traversal for related topics
- Support full-text search across knowledge base
- Track bidirectional link relationships


### 3. People Network Manager

**Purpose**: Manage person profiles and relationship connections.

**Interfaces**:
```python
class PeopleManager:
    def create_person(name: str, metadata: dict) -> Path
    def update_person(person_id: str, updates: dict) -> bool
    def link_to_knowledge(person_id: str, knowledge_id: str, context: str) -> bool
    def link_people(person1_id: str, person2_id: str, relationship: str) -> bool
    def get_person_network(person_id: str) -> dict
    def find_expertise(topic: str) -> List[dict]
```

**Responsibilities**:
- Create and update person markdown files
- Maintain person-to-knowledge wikilinks
- Track person-to-person relationships
- Support expertise discovery via knowledge connections
- Provide relationship context and history

### 4. Time Intelligence Engine

**Purpose**: Track work time, analyze patterns, provide estimates.

**Interfaces**:
```python
class TimeIntelligence:
    def start_work(description: str, knowledge_refs: List[str], people_refs: List[str]) -> str
    def end_work(work_id: str, completion_notes: str) -> TimeEntry
    def record_distraction(work_id: str, distraction_type: str, duration: int) -> bool
    def get_estimate(work_description: str, work_type: str) -> EstimateResult
    def analyze_patterns(days: int = 30, filters: dict = None) -> AnalysisResult
    def suggest_breakdown(work_description: str) -> List[WorkChunk]
```

**Responsibilities**:
- Record time entries with start/end timestamps
- Link time data to knowledge areas and people
- Analyze historical patterns for estimation
- Identify distraction patterns and impact
- Suggest work breakdown based on complexity
- Calculate estimation accuracy over time


### 5. Wikilink Parser & Resolver

**Purpose**: Parse, validate, and resolve wikilink references.

**Interfaces**:
```python
class WikilinkResolver:
    def parse_wikilinks(content: str) -> List[WikiLink]
    def resolve_link(link_text: str) -> Optional[Path]
    def validate_links(doc_path: Path) -> List[BrokenLink]
    def get_backlinks(target: str) -> List[BackLink]
    def suggest_links(content: str) -> List[str]
```

**Responsibilities**:
- Extract [[wikilink]] syntax from markdown
- Resolve links to actual file paths
- Detect broken or ambiguous links
- Track bidirectional relationships
- Suggest potential links based on content analysis

## Data Models

### Knowledge Document

```yaml
---
title: "API Design Patterns"
created_date: 2025-12-03
updated_date: 2025-12-03
tags:
  - api
  - architecture
  - design-patterns
related_people:
  - "[[John]]"
  - "[[Sarah]]"
time_invested: 240  # minutes
---

# API Design Patterns

## Overview
[Content with [[wikilinks]] to other knowledge]

## Key Concepts
- REST principles
- GraphQL considerations
- Related: [[Microservices Architecture]]

## People Context
Discussed with [[John]] during architecture review.
[[Sarah]] provided feedback on implementation.
```


### Person Profile

```yaml
---
name: "John Smith"
role: "Senior Architect"
team: "Platform Engineering"
created_date: 2025-12-03
updated_date: 2025-12-03
expertise_areas:
  - "[[API Design Patterns]]"
  - "[[Microservices Architecture]]"
  - "[[Database Design]]"
relationships:
  - person: "[[Sarah Johnson]]"
    type: "collaborator"
    context: "Work together on platform initiatives"
  - person: "[[Mike Chen]]"
    type: "reports_to"
    context: "Direct manager"
total_collaboration_time: 1200  # minutes
---

# John Smith

## Overview
Senior architect focused on platform scalability and API design.

## Recent Interactions
- 2025-12-01: Architecture review for [[New Payment API]]
- 2025-11-28: Discussed [[Database Sharding Strategy]]

## Expertise
Strong background in [[Distributed Systems]] and [[API Design Patterns]].
```

### Time Entry

```json
{
  "id": "time_20251203_001",
  "start_time": "2025-12-03T09:00:00Z",
  "end_time": "2025-12-03T11:30:00Z",
  "duration_minutes": 150,
  "work_description": "Design API endpoints for payment service",
  "work_type": "technical",
  "knowledge_refs": [
    "API Design Patterns",
    "Payment Systems"
  ],
  "people_refs": [
    "John Smith",
    "Sarah Johnson"
  ],
  "distractions": [
    {
      "type": "meeting",
      "duration_minutes": 15,
      "description": "Unscheduled sync"
    }
  ],
  "completion_percentage": 75,
  "notes": "Made good progress on endpoint design. Need to review auth flow."
}
```


### Work Breakdown

```json
{
  "original_work": "Implement new payment API",
  "estimated_total": 480,
  "chunks": [
    {
      "id": "chunk_1",
      "description": "Design API endpoints and data models",
      "estimated_minutes": 120,
      "work_type": "technical",
      "knowledge_refs": ["API Design Patterns"],
      "dependencies": []
    },
    {
      "id": "chunk_2",
      "description": "Implement authentication and authorization",
      "estimated_minutes": 180,
      "work_type": "technical",
      "knowledge_refs": ["Security Patterns", "OAuth"],
      "dependencies": ["chunk_1"]
    },
    {
      "id": "chunk_3",
      "description": "Write integration tests",
      "estimated_minutes": 120,
      "work_type": "technical",
      "knowledge_refs": ["Testing Strategies"],
      "dependencies": ["chunk_2"]
    },
    {
      "id": "chunk_4",
      "description": "Documentation and deployment guide",
      "estimated_minutes": 60,
      "work_type": "writing",
      "knowledge_refs": ["API Documentation"],
      "dependencies": ["chunk_3"]
    }
  ]
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Knowledge Base Properties

**Property 1: Wikilink Bidirectionality**
*For any* two knowledge documents A and B, if A contains a wikilink to B, then B's backlinks must include A
**Validates: Requirements 1.2**

**Property 2: Knowledge Document Storage Format**
*For any* knowledge document created, the stored file must be valid markdown with parseable YAML frontmatter
**Validates: Requirements 1.1**

**Property 3: Complete Link Display**
*For any* knowledge document, viewing it must return all incoming and outgoing wikilinks that exist in the system
**Validates: Requirements 1.3**

**Property 4: Search Ranking Consistency**
*For any* search query, documents with more connections to the query topic must rank higher than documents with fewer connections
**Validates: Requirements 1.4**

**Property 5: Graph Traversal Completeness**
*For any* knowledge document, requesting related topics must return all documents within the specified graph distance
**Validates: Requirements 1.5**


### People Network Properties

**Property 6: Person Profile Storage Format**
*For any* person profile created, the stored file must be valid markdown with parseable YAML frontmatter
**Validates: Requirements 2.1**

**Property 7: Person-Knowledge Link Bidirectionality**
*For any* person P and knowledge document K, if P is linked to K, then K's related_people must include P
**Validates: Requirements 2.2**

**Property 8: Relationship Metadata Preservation**
*For any* person-to-person link created, the relationship type and context must be stored and retrievable
**Validates: Requirements 2.3**

**Property 9: Complete Connection Display**
*For any* person profile, viewing it must return all connected knowledge documents and people relationships
**Validates: Requirements 2.4**

**Property 10: Expertise Discovery Accuracy**
*For any* expertise search query, all people connected to relevant knowledge topics must be included in results
**Validates: Requirements 2.5**

### Notes Processing Properties

**Property 11: Inbox Preservation**
*For any* content added to the Notes Inbox, the raw text must remain unmodified until explicit processing is requested
**Validates: Requirements 3.1**

**Property 12: Entity Detection Completeness**
*For any* note containing knowledge topics or people mentions, batch processing must identify all entities
**Validates: Requirements 3.2**

**Property 13: Knowledge Creation from Notes**
*For any* identified knowledge topic in notes, the system must create or update the corresponding knowledge document with appropriate wikilinks
**Validates: Requirements 3.3**

**Property 14: People Update from Notes**
*For any* identified person mention in notes, the system must update the person profile and create appropriate connections
**Validates: Requirements 3.4**

**Property 15: Inbox Cleanup Completeness**
*For any* batch processing completion, the Notes Inbox must be cleared and a summary of all updates must be provided
**Validates: Requirements 3.5**


### Interactive Processing Properties

**Property 16: Ambiguity Detection**
*For any* note with ambiguous content, the system must ask clarifying questions before creating updates
**Validates: Requirements 4.2**

**Property 17: Missing Context Detection**
*For any* note with incomplete information, the system must prompt for additional context
**Validates: Requirements 4.3**

**Property 18: Clarification Incorporation**
*For any* clarification provided by the user, the system must incorporate it into the resulting knowledge or people updates
**Validates: Requirements 4.4**

### Conversational Capture Properties

**Property 19: Conversational Entity Detection**
*For any* information shared in conversation, the system must analyze and identify knowledge topics and people mentions
**Validates: Requirements 5.1**

**Property 20: Conversational Clarification**
*For any* potential update identified in conversation, the system must ask clarifying questions before proposing updates
**Validates: Requirements 5.2**

**Property 21: Update Proposal Accuracy**
*For any* conversation with sufficient context, the system must propose specific and accurate knowledge or people updates
**Validates: Requirements 5.3**

**Property 22: Confirmed Update Application**
*For any* user-confirmed update, the system must create or update the relevant documents with correct wikilinks
**Validates: Requirements 5.4**

### Meeting Notes Properties

**Property 23: Meeting Data Capture**
*For any* meeting notes session, the system must capture all attendees, topics, and key points
**Validates: Requirements 6.1**

**Property 24: Meeting Knowledge Extraction**
*For any* finalized meeting notes, the system must identify all knowledge topics and create or update relevant documents
**Validates: Requirements 6.2**

**Property 25: Meeting People Updates**
*For any* finalized meeting notes mentioning people, the system must update person profiles with meeting context
**Validates: Requirements 6.3**

**Property 26: Meeting Connection Graph**
*For any* processed meeting notes, the system must create wikilinks between all attendees, topics, and related knowledge
**Validates: Requirements 6.4**

**Property 27: Meeting Connection Display**
*For any* meeting notes viewed, the system must display all connections to the broader knowledge base and people network
**Validates: Requirements 6.5**


### Time Tracking Properties

**Property 28: Time Entry Creation**
*For any* work start action, the system must create a time entry with correct start timestamp and work description
**Validates: Requirements 7.1**

**Property 29: Duration Calculation**
*For any* work completion, the system must record the end timestamp and calculate duration as (end_time - start_time)
**Validates: Requirements 7.2**

**Property 30: Work Categorization Storage**
*For any* categorized work, the system must store the work type and all related knowledge/people tags
**Validates: Requirements 7.3**

**Property 31: Distraction Data Capture**
*For any* recorded distraction, the system must capture the interruption type and duration
**Validates: Requirements 7.4, 10.1**

**Property 32: Time History Query Completeness**
*For any* time history request with filters, the system must return all matching time entries
**Validates: Requirements 7.5**

### Time Intelligence Properties

**Property 33: Similar Work Identification**
*For any* new work description, the system must identify all historical work with matching type and knowledge connections
**Validates: Requirements 8.1**

**Property 34: Statistical Calculation Accuracy**
*For any* set of similar historical work, the system must correctly calculate average duration and variance
**Validates: Requirements 8.2**

**Property 35: Estimate Range Provision**
*For any* estimate request, the system must provide a time range based on historical patterns (e.g., mean ± std dev)
**Validates: Requirements 8.3**

**Property 36: Estimate Explanation Transparency**
*For any* provided estimate, the system must explain which historical work items informed the calculation
**Validates: Requirements 8.4**

**Property 37: Estimation Accuracy Analysis**
*For any* estimation insights request, the system must identify patterns in estimation accuracy and common deviations
**Validates: Requirements 8.5**


### Work Breakdown Properties

**Property 38: Complexity Analysis**
*For any* work description, the system must analyze and identify complexity indicators
**Validates: Requirements 9.1**

**Property 39: Breakdown Suggestion Logic**
*For any* complex work item, the system must suggest logical breakdown points based on work type
**Validates: Requirements 9.2**

**Property 40: Chunk Estimation**
*For any* suggested breakdown, the system must provide time estimates for each chunk
**Validates: Requirements 9.3**

**Property 41: Breakdown Time Entry Creation**
*For any* accepted breakdown, the system must create separate time tracking entries for each chunk
**Validates: Requirements 9.4**

**Property 42: Breakdown Aggregation**
*For any* completed breakdown chunks, the system must aggregate actual time and compare to original estimates
**Validates: Requirements 9.5**

### Distraction Analysis Properties

**Property 43: Distraction Pattern Identification**
*For any* distraction analysis request, the system must identify patterns by time of day, day of week, and work type
**Validates: Requirements 10.2**

**Property 44: Distraction Impact Calculation**
*For any* distraction analysis, the system must calculate the impact on work duration
**Validates: Requirements 10.3**

**Property 45: Distraction Overhead in Estimates**
*For any* time estimate, the system must factor in typical distraction overhead for the work type
**Validates: Requirements 10.5**

### Integration Properties

**Property 46: Time-Knowledge Link Creation**
*For any* time entry linked to knowledge, the system must create verifiable connections between time data and knowledge documents
**Validates: Requirements 11.1**

**Property 47: Knowledge Time Investment Display**
*For any* knowledge document, viewing it must display the total time invested in that topic
**Validates: Requirements 11.2**

**Property 48: Expertise Ranking by Time**
*For any* expertise analysis request, the system must rank knowledge areas by total time investment
**Validates: Requirements 11.3**

**Property 49: Time Grouping and Trends**
*For any* time report request, the system must group time by knowledge area and show trends over time
**Validates: Requirements 11.4**

**Property 50: Experience-Adjusted Estimates**
*For any* estimate suggestion, the system must consider the user's experience level in related knowledge areas
**Validates: Requirements 11.5**


**Property 51: Time-People Link Creation**
*For any* time entry linked to people, the system must create verifiable connections between time data and person profiles
**Validates: Requirements 12.1**

**Property 52: Person Collaboration Time Display**
*For any* person profile, viewing it must display the total time spent on work involving that person
**Validates: Requirements 12.2**

**Property 53: Collaboration Pattern Identification**
*For any* collaboration analysis request, the system must identify frequent collaborators and time patterns
**Validates: Requirements 12.3**

**Property 54: Collaboration-Adjusted Estimates**
*For any* work estimate involving specific people, the system must factor in historical collaboration time
**Validates: Requirements 12.4**

**Property 55: Work Type Categorization**
*For any* time analysis, the system must correctly distinguish between solo work and collaborative work
**Validates: Requirements 12.5**

### Migration Properties

**Property 56: Knowledge Document Preservation**
*For any* migration execution, all existing Knowledge documents must remain unmodified
**Validates: Requirements 13.1**

**Property 57: People Profile Preservation**
*For any* migration execution, all existing People profiles must remain unmodified
**Validates: Requirements 13.2**

**Property 58: Task Time Conversion**
*For any* task with time estimates, migration must convert them to time tracking history entries
**Validates: Requirements 13.3**


## Error Handling

### Input Validation Errors

**Invalid Wikilink Syntax**
- Detection: Parse wikilinks and identify malformed syntax
- Response: Log warning, suggest correction, continue processing
- User Feedback: "Found malformed wikilink: [[incomplete - did you mean [[Complete Topic]]?"

**Missing Required Metadata**
- Detection: Validate YAML frontmatter against schema
- Response: Use defaults for optional fields, prompt for required fields
- User Feedback: "Knowledge document missing 'title' field. Please provide a title."

**Circular Wikilink References**
- Detection: Graph traversal with cycle detection
- Response: Allow circular references (they're valid), but limit traversal depth
- User Feedback: None (circular references are acceptable in knowledge graphs)

### Processing Errors

**Ambiguous Entity References**
- Detection: Multiple matches for person/knowledge names
- Response: Present options to user for disambiguation
- User Feedback: "Found multiple matches for 'John': [[John Smith]], [[John Doe]]. Which did you mean?"

**File System Errors**
- Detection: Permission denied, disk full, file locked
- Response: Retry with exponential backoff, fallback to temp storage
- User Feedback: "Unable to save knowledge document. Retrying... (attempt 2/3)"

**Concurrent Modification**
- Detection: File modified between read and write
- Response: Merge changes if possible, otherwise prompt user
- User Feedback: "This document was modified by another process. Review changes before saving."


### Data Integrity Errors

**Broken Wikilinks**
- Detection: Periodic validation of all wikilinks
- Response: Generate report of broken links, suggest fixes
- User Feedback: "Found 3 broken wikilinks. Run 'fix-links' to review and repair."

**Orphaned Documents**
- Detection: Documents with no incoming or outgoing links
- Response: Flag for review, suggest potential connections
- User Feedback: "Document 'Old Notes' has no connections. Consider linking or archiving."

**Time Entry Inconsistencies**
- Detection: End time before start time, negative durations
- Response: Reject entry, prompt for correction
- User Feedback: "Invalid time entry: end time (2:00 PM) is before start time (3:00 PM)"

### Recovery Strategies

**Graceful Degradation**
- If wikilink resolution fails, display raw link text
- If time analysis fails, return basic statistics without patterns
- If entity detection fails, process as plain text

**Transaction Rollback**
- Batch operations use transaction-like semantics
- On failure, rollback all changes in the batch
- Preserve original state and log error details

**Backup and Restore**
- Automatic backups before major operations (migration, batch processing)
- User-initiated backup command available
- Restore from backup with conflict resolution


## Testing Strategy

### Unit Testing

Unit tests will verify specific functionality of individual components:

**Knowledge Manager Tests**
- Create knowledge document with valid YAML
- Parse wikilinks from markdown content
- Resolve wikilinks to file paths
- Handle malformed wikilink syntax
- Search knowledge by keywords

**People Manager Tests**
- Create person profile with metadata
- Link person to knowledge document
- Link two people with relationship type
- Query person network
- Find expertise by topic

**Time Intelligence Tests**
- Create time entry with timestamps
- Calculate duration correctly
- Handle timezone conversions
- Aggregate time by category
- Calculate basic statistics (mean, variance)

**Wikilink Resolver Tests**
- Parse [[wikilink]] syntax
- Handle [[link|display text]] format
- Detect broken links
- Build backlink index
- Suggest potential links

### Property-Based Testing

Property-based tests will verify universal properties across all inputs using **Hypothesis** (Python property testing library). Each test will run a minimum of 100 iterations with randomly generated inputs.


**Property Test Requirements**:
- Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document
- Tag format: `# Feature: knowledge-time-system, Property {number}: {property_text}`
- Each correctness property must be implemented by a single property-based test
- Tests must be placed as close to implementation as possible to catch errors early

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: knowledge-time-system, Property 1: Wikilink Bidirectionality
@given(
    doc_a=st.text(min_size=1),
    doc_b=st.text(min_size=1)
)
def test_wikilink_bidirectionality(doc_a, doc_b):
    """For any two documents A and B, if A links to B, then B's backlinks include A"""
    # Create document A with link to B
    km = KnowledgeManager()
    km.create_knowledge(doc_a, f"Content with [[{doc_b}]]", [])
    
    # Verify B's backlinks include A
    backlinks = km.get_backlinks(doc_b)
    assert doc_a in [bl['source'] for bl in backlinks]
```

**Property Test Coverage**:
- Properties 1-5: Knowledge Base (wikilinks, storage, search, traversal)
- Properties 6-10: People Network (profiles, links, relationships)
- Properties 11-15: Batch Notes Processing (entity detection, updates)
- Properties 16-18: Interactive Processing (ambiguity, clarifications)
- Properties 19-22: Conversational Capture (real-time processing)
- Properties 23-27: Meeting Notes (capture, extraction, connections)
- Properties 28-32: Time Tracking (entries, duration, categorization)
- Properties 33-37: Time Intelligence (similarity, estimates, accuracy)
- Properties 38-42: Work Breakdown (complexity, chunks, aggregation)
- Properties 43-45: Distraction Analysis (patterns, impact, overhead)
- Properties 46-55: Integration (time-knowledge, time-people links)
- Properties 56-58: Migration (preservation, conversion)


### Integration Testing

Integration tests will verify end-to-end workflows:

**Notes to Knowledge Workflow**
- Add notes to inbox file
- Process notes (batch or interactive)
- Verify knowledge documents created
- Verify wikilinks established
- Verify inbox cleared

**Meeting Notes Workflow**
- Capture meeting with attendees and topics
- Finalize meeting notes
- Verify knowledge documents updated
- Verify person profiles updated
- Verify all connections created

**Time Tracking Workflow**
- Start work with description
- Record distractions
- Complete work
- Verify time entry created
- Verify duration calculated
- Request estimate for similar work
- Verify estimate uses historical data

**Work Breakdown Workflow**
- Describe complex work
- Request breakdown
- Accept breakdown
- Complete chunks
- Verify aggregation and comparison

### Test Data Generation

**Generators for Property Tests**:
- `gen_knowledge_title()`: Valid knowledge document titles
- `gen_person_name()`: Valid person names
- `gen_wikilink()`: Valid wikilink syntax
- `gen_work_description()`: Realistic work descriptions
- `gen_time_entry()`: Valid time entry data
- `gen_meeting_notes()`: Realistic meeting note content

**Constraints**:
- Knowledge titles: 1-200 characters, no special chars in filenames
- Person names: 1-100 characters, valid for file paths
- Wikilinks: Must match existing documents or be flagged as broken
- Time entries: Start time < end time, duration > 0
- Work descriptions: 10-500 characters, contain actionable content


## Implementation Notes

### Technology Stack

**Core Language**: Python 3.10+
- Existing MCP server infrastructure
- Rich ecosystem for text processing and data analysis
- Hypothesis library for property-based testing

**Storage**: Markdown files with YAML frontmatter
- Human-readable and editable
- Git-friendly for version control
- Obsidian-compatible for visualization

**Data Formats**:
- Knowledge/People: Markdown + YAML frontmatter
- Time data: JSON files for structured queries
- Configuration: YAML (config.yaml)

**Key Libraries**:
- `pyyaml`: YAML parsing
- `markdown`: Markdown processing
- `hypothesis`: Property-based testing
- `mcp`: MCP server framework
- `pathlib`: File system operations
- `datetime`: Time handling

### Migration Strategy

**Core Principle**: This is an **update, not a rewrite**. The existing WorkOS structure, agent context, and learned patterns are retained and enhanced. The agent keeps all knowledge about the user, work patterns, and interaction preferences - only the task management functionality is being repurposed into knowledge and time intelligence.

**What Stays the Same**:
- **All agent context and learned patterns**: Interaction style, user preferences, work domain knowledge
- **All existing content**: Knowledge/, People/, daily-notes/, .system/
- Directory structure: Knowledge/, People/, .system/, core/mcp/
- MCP server architecture (server.py)
- Markdown + YAML frontmatter format
- Python codebase and dependencies
- Obsidian compatibility
- Git version control
- **CLAUDE.md personality and interaction guidelines**

**What Changes**:
- BACKLOG.md → NOTES_INBOX.md (renamed, same purpose)
- Tasks/ directory → Kept for reference, no longer actively managed
- CLAUDE.md → Updated with new agent instructions
- config.yaml → Updated with new settings (remove task priorities, add time tracking config)
- MCP tools → Modified to focus on knowledge/time instead of tasks

**Phase 1: Preserve Existing Data**
1. Backup current system state to backups/
2. Verify Knowledge/ and People/ directories intact
3. No modifications to existing documents
4. Keep all task files in Tasks/ for historical reference

**Phase 2: Rename and Document**
1. Rename BACKLOG.md to NOTES_INBOX.md
2. **Update (not rewrite) CLAUDE.md**:
   - Preserve: Interaction style, user preferences, communication patterns
   - Preserve: Knowledge about user's work context and domain
   - Preserve: Learned patterns about how user likes to work
   - Update: Tool descriptions and workflows (task management → knowledge/time management)
   - Update: Command examples and prompts
   - Add: New capabilities (knowledge graph, time intelligence, work breakdown)
   - Keep: All personality and interaction guidelines
3. Update config.yaml:
   - Preserve: User-specific settings and preferences
   - Remove: task categories, priority limits, task aging
   - Add: time tracking settings, work types, distraction categories
   - Migrate: Relevant category keywords to work types
4. Update docs/README.md with new system description
5. **Preserve all context in**:
   - Knowledge/ directory (all existing notes and context)
   - People/ directory (all relationship context)
   - daily-notes/ (all historical context about work patterns)
   - .system/session_tracker.json (current session context)

**Phase 3: Convert Task Data to Time History**
1. Read all task files from Tasks/
2. Extract time estimates and actual time spent from task metadata
3. Create time_analytics.json entries from historical task data
4. Preserve task files in Tasks/ for reference (don't delete)
5. Add note to Tasks/README.md explaining the directory is now read-only

**Phase 4: Modify MCP Server**
1. Keep existing server.py structure
2. Add new tools: create_knowledge, link_knowledge, start_work, end_work, etc.
3. Modify existing tools: process_backlog → process_notes_inbox
4. Mark task-specific tools as deprecated but keep functional
5. Update tool descriptions and schemas

**Phase 5: Validation**
1. Run property tests on migrated data
2. Verify wikilinks are intact in Knowledge/ and People/
3. Verify time data is accessible via new tools
4. Test notes processing with sample data
5. Generate migration report with summary of changes


### Performance Considerations

**Wikilink Resolution**
- Cache resolved links in memory
- Rebuild cache on file system changes
- Use file system watchers for incremental updates

**Search Performance**
- Build inverted index for full-text search
- Update index incrementally on document changes
- Limit search results to top 50 by default

**Time Analysis**
- Pre-aggregate common queries (daily, weekly, monthly)
- Cache statistical calculations
- Limit historical analysis to configurable time window (default 90 days)

**Graph Traversal**
- Limit traversal depth to prevent infinite loops
- Cache frequently accessed paths
- Use breadth-first search for related topics

### Security and Privacy

**File System Access**
- Restrict operations to BASE_DIR and subdirectories
- Validate all file paths to prevent directory traversal
- Use safe file naming (sanitize user input)

**Data Privacy**
- All data stored locally (no external services)
- No telemetry or analytics sent externally
- User controls all data and backups

**Backup Strategy**
- Automatic backups before destructive operations
- User-initiated backups available
- Backup retention configurable (default 30 days)

### Extensibility

**Plugin Architecture**
- Custom entity extractors (e.g., project names, technologies)
- Custom wikilink resolvers (e.g., external references)
- Custom time analysis algorithms
- Custom export formats

**API Design**
- All core functionality exposed via MCP tools
- Clear separation between business logic and MCP layer
- Testable without MCP server running

