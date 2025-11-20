---
inclusion: always
---

# Meeting Notes Workflow

## Meeting Notes Template

When creating meeting notes, use this structure:

```markdown
# [Meeting Topic] - [Date]

## Meeting Info
- **Date:** YYYY-MM-DD
- **Topic:** [Meeting purpose]
- **Attendees:** 
  - [Name] ([role/context])
  - [Name] ([role/context])

## Notes

### [Topic 1]
- Key points
- Decisions made
- Discussion highlights

### [Topic 2]
- Key points
- Decisions made

## Action Items
- [ ] [Action item with owner]
- [ ] [Action item with owner]

## Follow-up
- [Any follow-up needed]

## Related
- [[Project: Name]]
- [[Person Name]]
- [[Task Name]]
```

## During Meeting

1. **Create meeting file** in Knowledge/ folder
   - Naming: `[Topic]-Meeting-YYYY-MM-DD.md`
   - Example: `Phoenix-UX-Meeting-2025-11-19.md`

2. **Capture notes in real-time**
   - Add attendees with roles/context
   - Group notes by topic/section
   - Note key decisions and discussion points
   - Capture action items as they come up

3. **Link people mentioned**
   - Add attendees to meeting info
   - Reference people in notes when relevant

## After Meeting

1. **Create tasks from action items**
   - Each action item becomes a task (if actionable)
   - Link task back to meeting notes in resource_refs
   - Set appropriate priority and due date

2. **Update person files**
   - Add meeting reference to attendees' person files
   - Update "Recent Topics" or "Notes" sections
   - Add any new context learned about the person

3. **Link to projects**
   - Add meeting to related project documentation
   - Update project status if needed

4. **Update related tasks**
   - If meeting discussed existing tasks, update their progress logs
   - Add meeting notes link to resource_refs

## Chat Commands

### Natural Meeting Capture
When you say you're "in a meeting" or similar phrases, I'll:
1. Ask for meeting topic (if not clear from context)
2. Create meeting notes file in Knowledge/
3. Enter note-taking mode - capture everything you share
4. When you indicate the meeting is over, I'll process the notes

**Trigger phrases I understand:**
- "in a meeting"
- "attending [meeting name]"
- "meeting for [topic]"
- "starting meeting"

**End phrases I understand:**
- "meeting is over"
- "meeting ended"
- "finished the meeting"
- "done with meeting"

**If unclear, I'll ask for clarification**

### Post-Meeting Processing
After meeting ends, I'll automatically:
1. Extract action items
2. Ask: Create tasks? Update person files? Link to projects?
3. Process your responses
4. Confirm all updates complete

### Manual Commands (if needed)
- "create meeting notes" or "start meeting notes for [topic]" - Creates template file
- "process meeting notes" or "finish meeting [topic]" - Extracts action items, updates person files, creates tasks

## File Organization

**Location:** `Knowledge/` folder

**Naming Convention:**
- `[Topic]-Meeting-YYYY-MM-DD.md`
- Examples:
  - `Phoenix-UX-Meeting-2025-11-19.md`
  - `WBR-Review-Meeting-2025-11-20.md`
  - `Customer-Call-Acme-2025-11-21.md`

**Linking:**
- Link to person files: `People/[Name].md`
- Link to tasks: `[[Task Name]]`
- Link to projects: `[[Project: Name]]`
- Link to other knowledge: `[[Doc Name]]`

## Best Practices

1. **Capture in real-time** - Don't wait until after the meeting
2. **Note decisions** - Highlight key decisions made
3. **Action items clear** - Each action item should have owner and be actionable
4. **Link liberally** - Connect to people, tasks, projects
5. **Update person files** - Keep relationship context current
6. **Create tasks promptly** - Don't let action items languish
7. **Use consistent naming** - Makes finding meetings easier

## Meeting Types

**1-1 Meetings:**
- Store in person's file reference section
- Update person file with topics discussed
- Link to relevant tasks/projects

**Project Meetings:**
- Store in Knowledge/ with project name
- Link to project documentation
- Update project status

**Customer Meetings:**
- Store in Knowledge/ with customer name
- Consider creating customer person file if recurring
- Link to customer-related tasks

**Team Meetings:**
- Store in Knowledge/ with team/topic name
- Distribute action items to task owners
- Update relevant project documentation
