---
inclusion: always
---

# WorkOS Advanced Features

## Goals Alignment
- **Always tie tasks to goals** - Every task Context section must reference GOALS.md
- **Be specific** - Quote goal sections or use specific headings from GOALS.md
- **Question goalless tasks** - If a task doesn't support any goal, ask why it should be done
- **Update as goals evolve** - When GOALS.md changes, review task alignment

## Deduplication Features

The system automatically:
- **Detects similar tasks** using fuzzy matching (60% similarity threshold)
- **Identifies ambiguous items** that need clarification
- **Suggests appropriate categories** based on keywords
- **Prevents duplicate creation** by flagging potential matches

When processing backlog:
1. Check for duplicates first with `process_backlog_with_dedup`
2. Ask clarifying questions for ambiguous items
3. Suggest category based on keywords
4. Create tasks only after confirming no duplicates

## Best Practices for Backlog Processing

1. **Process ONE item at a time** - Don't batch create without user confirmation
2. **Ask context questions** - If not provided, ask:
   - What's it related to? (larger initiative/project)
   - Any dependencies? (what it depends on or blocks)
   - Why now? (timing rationale)
3. **Ask minimal other questions** - Only what's needed to resolve ambiguity
4. **Suggest defaults** - Offer category/priority suggestions based on content
5. **Check duplicates first** - Always use deduplication before creating
6. **Tie to goals immediately** - Write Context section referencing GOALS.md
7. **Estimate time** - Provide realistic time estimates in minutes
8. **Link resources** - Add relevant files from consolidated knowledgebase to resource_refs
9. **Auto-link people** - If person mentioned, add to resource_refs and update their person file

## People Management

When creating or updating tasks:
- **Detect person mentions** - Look for names in task content
- **Add to resource_refs** - Include People/[Name].md in task frontmatter
- **Update person file** - Add task to person's "Related Tasks/Projects" section
- **Use Obsidian links** - Format as [[Task Name]] or [[Person Name]] for easy navigation
- **Bidirectional linking** - Ensure both task and person file reference each other

## Interaction Style

- Be direct, friendly, and concise
- Batch follow-up questions when processing backlog
- Always tie tasks to goals in the Context section
- Process backlog items ONE AT A TIME interactively
- Suggest no more than 3 focus tasks for daily work
