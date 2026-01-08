# Notes Processing MCP Tools

This document describes the MCP server tools for notes processing in the WorkOS knowledge and time intelligence system.

## Overview

The notes processing tools enable the system to transform raw notes from multiple input sources into structured knowledge documents and person profiles. These tools support:

- **Batch processing** from the Notes Inbox file
- **Interactive processing** with clarifying questions
- **Real-time conversational capture** during agent interactions
- **Meeting notes integration** with automatic entity extraction

## Tools

### 1. process_notes_inbox

**Description**: Process notes from the Notes Inbox file in batch mode. Extracts entities, creates/updates knowledge and people documents, then clears the inbox.

**Input Schema**:
```json
{
  "notes_file": "string (optional)" // Path to notes file, defaults to NOTES_INBOX.md
}
```

**Output**:
```json
{
  "success": true,
  "processed_count": 5,
  "summary": "Processed 5 notes. Created 3 knowledge documents. Updated 2 person profiles.",
  "applied_updates": {
    "knowledge_created": ["API Design", "GraphQL Patterns"],
    "knowledge_updated": ["Database Optimization"],
    "people_created": ["John"],
    "people_updated": ["Sarah"],
    "errors": []
  },
  "processing_errors": []
}
```

**Use Cases**:
- Process accumulated notes at end of day
- Batch import notes from external sources
- Clean up inbox after capturing notes offline

**Requirements Validated**: 3.1, 3.2, 3.3, 3.4, 3.5

---

### 2. process_notes_interactive

**Description**: Start an interactive notes processing session. Presents notes one at a time, asks clarifying questions, and waits for user confirmation.

**Input Schema**:
```json
{
  "notes_file": "string (optional)" // Path to notes file, defaults to NOTES_INBOX.md
}
```

**Output**:
```json
{
  "success": true,
  "session_id": "uuid-string",
  "total_notes": 5,
  "current_index": 0,
  "message": "Interactive session started with 5 notes to process"
}
```

**Use Cases**:
- Process notes with ambiguous content
- Ensure high-quality knowledge capture
- Review and confirm updates before applying

**Requirements Validated**: 4.1

---

### 3. process_interactive_note

**Description**: Process the next note in an interactive session. Extracts entities, detects ambiguities, and generates clarification questions.

**Input Schema**:
```json
{
  "session_id": "string (required)",
  "clarifications": {
    "question1": "answer1",
    "question2": "answer2"
  },
  "confirmed": false,
  "advance": false
}
```

**Output** (when processing note):
```json
{
  "success": true,
  "session_id": "uuid-string",
  "note_index": 0,
  "note_text": "Met with John to discuss API Design",
  "note_type": "mixed",
  "requires_clarification": true,
  "clarification_questions": [
    "Which John did you mean? (Multiple people found)",
    "Is 'API Design' a new topic or related to existing knowledge?"
  ],
  "entities": [
    {
      "type": "person",
      "value": "John",
      "context": "Met with John to discuss",
      "confidence": 0.8,
      "ambiguous": true
    }
  ],
  "remaining_notes": 4
}
```

**Output** (when applying updates):
```json
{
  "success": true,
  "session_id": "uuid-string",
  "updates_applied": true,
  "note_index": 0,
  "applied_updates": [
    "Created knowledge: API Design",
    "Updated person: John"
  ],
  "errors": []
}
```

**Workflow**:
1. Call with `session_id` to process current note
2. If `requires_clarification`, provide `clarifications` and call again
3. Set `confirmed: true` to apply updates
4. Set `advance: true` to move to next note

**Use Cases**:
- Step through notes one at a time
- Provide clarifications for ambiguous content
- Confirm updates before applying

**Requirements Validated**: 4.2, 4.3, 4.4, 4.5

---

### 4. process_conversational_note

**Description**: Process a note from real-time conversation. Analyzes content, detects entities, asks clarifying questions, and proposes updates.

**Input Schema**:
```json
{
  "note_text": "string (required)",
  "context": {
    "previous_entities": []
  },
  "apply_updates": false,
  "proposed_updates": []
}
```

**Output** (when analyzing):
```json
{
  "success": true,
  "entities_detected": [
    {
      "type": "knowledge",
      "value": "Kubernetes",
      "context": "Learned about Kubernetes deployment",
      "confidence": 0.9,
      "ambiguous": false
    }
  ],
  "clarification_questions": [
    "Is 'Kubernetes' a new topic, or is it related to something you've mentioned before?"
  ],
  "proposed_updates": [
    {
      "action": "create_knowledge",
      "title": "Kubernetes",
      "content": "Learned about Kubernetes deployment strategies"
    }
  ],
  "requires_confirmation": true
}
```

**Output** (when applying):
```json
{
  "success": true,
  "updates_applied": true,
  "applied_updates": [
    "Created knowledge: Kubernetes",
    "Updated person: DevOps Team"
  ],
  "errors": [],
  "message": "Applied 2 updates"
}
```

**Workflow**:
1. Call with `note_text` to analyze
2. Review `clarification_questions` and `proposed_updates`
3. Call again with `apply_updates: true` and `proposed_updates` to apply

**Use Cases**:
- Capture knowledge during conversation
- Real-time entity detection
- Immediate knowledge base updates

**Requirements Validated**: 5.1, 5.2, 5.3, 5.4, 5.5

---

### 5. process_meeting_notes

**Description**: Process meeting notes with attendees and topics. Extracts knowledge, updates person profiles, and creates connections.

**Input Schema**:
```json
{
  "attendees": ["Alice", "Bob", "Charlie"],
  "topics": ["API Design", "Database Schema"],
  "notes": "string (required)",
  "date": "2025-12-04T10:00:00Z (optional)"
}
```

**Output**:
```json
{
  "success": true,
  "meeting_id": "meeting_20251204_100000",
  "summary": "Processed meeting with 3 attendees and 2 topics",
  "applied_updates": {
    "knowledge_created": ["API Design"],
    "knowledge_updated": ["Database Schema"],
    "people_updated": ["Alice", "Bob", "Charlie"],
    "connections_created": [
      "Alice -> API Design",
      "Bob -> API Design",
      "Charlie -> Database Schema"
    ],
    "errors": []
  }
}
```

**Use Cases**:
- Process meeting notes automatically
- Link attendees to discussed topics
- Build meeting knowledge graph

**Requirements Validated**: 6.1, 6.2, 6.3, 6.4, 6.5

---

## Migration from Old Tools

### process_backlog → process_notes_inbox

The old `process_backlog` tool has been deprecated in favor of `process_notes_inbox`. The new tool:

- Uses the same file (NOTES_INBOX.md, formerly BACKLOG.md)
- Provides entity extraction and knowledge/people updates
- Clears the inbox after processing
- Returns structured results with applied updates

**Migration**:
```javascript
// Old
await callTool('process_backlog', {});

// New
await callTool('process_notes_inbox', {});
```

---

## Entity Types

The notes processor extracts the following entity types:

### Knowledge Topics
- Explicit wikilinks: `[[Topic Name]]`
- Capitalized phrases near knowledge keywords
- Topics discussed in meetings

### People
- Explicit wikilinks: `[[Person Name]]`
- @mentions: `@alice`
- Phrases like "met with", "discussed with", "worked with"

### Time References
- Duration patterns: "2 hours", "30 minutes"
- Used for time tracking integration

---

## Clarification Questions

The system generates clarification questions when:

1. **Ambiguous entities**: Multiple matches found (e.g., multiple people named "John")
2. **Low confidence**: Entity detection confidence < 0.7
3. **Missing context**: Note is too brief or vague
4. **Unclear references**: Pronouns without clear antecedents

---

## Best Practices

### Batch Processing
- Use for end-of-day inbox cleanup
- Good for offline note capture
- Fast but less accurate than interactive

### Interactive Processing
- Use when notes contain ambiguous content
- Ensures high-quality knowledge capture
- Takes more time but produces better results

### Conversational Processing
- Use during live agent interactions
- Immediate feedback and clarification
- Best for real-time knowledge building

### Meeting Notes
- Capture attendees and topics explicitly
- Include context in notes text
- Creates rich connection graph automatically

---

## Error Handling

All tools return structured error information:

```json
{
  "success": false,
  "error": "Error message",
  "processing_errors": ["Detailed error 1", "Detailed error 2"]
}
```

Common errors:
- File not found (notes_file doesn't exist)
- Session not found (invalid session_id)
- Entity extraction failures (malformed content)
- Knowledge/people update failures (file system errors)

---

## Testing

Integration tests are available in:
- `test_notes_mcp_integration.py` - MCP tool integration tests
- `test_notes_properties.py` - Property-based tests for correctness

Run tests:
```bash
pytest core/test_notes_mcp_integration.py -v
pytest core/test_notes_properties.py -v
```

---

## Implementation Details

### Components
- `NotesProcessor` - Core notes processing engine
- `KnowledgeManager` - Knowledge document management
- `PeopleManager` - Person profile management
- `WikilinkResolver` - Wikilink parsing and resolution

### Storage
- Knowledge documents: `Knowledge/*.md`
- Person profiles: `People/*.md`
- Notes inbox: `NOTES_INBOX.md`

### Session Management
Interactive sessions are stored in memory on the `notes_processor` instance. In production, consider using persistent session storage.

---

## Future Enhancements

Potential improvements:
1. Persistent session storage for interactive processing
2. Batch clarification mode (collect all questions, then answer)
3. Automatic entity disambiguation using context
4. Machine learning for entity confidence scoring
5. Integration with external knowledge sources
