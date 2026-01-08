---
inclusion: always
---

# WorkOS Context & Knowledge Management

## Knowledge Management

### File Organization
- **Topics/**: Subject-based knowledge documents
- **Daily/**: Daily notes, closeouts, and retrospectives
- **Context/**: Background materials and reference documents
- **Templates/**: Process guides and templates
- **Resources/**: Reference materials and tools
- **Active/**: Current work tracking

### Linking Strategy
- Use `[[Note Name]]` for internal links between notes (Obsidian wikilinks)
- Use `#tag` for categorization
- Reference files with relative paths when needed
- Keep related notes linked for easy navigation

### Knowledge Creation
- Always add source attribution: `<!-- Source: workOS Agent - YYYY-MM-DD -->`
- Link to related people and tasks
- Use consistent naming conventions

## People Management

When creating or updating tasks:
- **Detect person mentions** - Look for names in task content
- **Add to resource_refs** - Include People/[Name].md in task frontmatter
- **Update person file** - Add task to person's "Related Tasks/Projects" section
- **Use Obsidian links** - Format as [[Task Name]] or [[Person Name]] for easy navigation
- **Bidirectional linking** - Ensure both task and person file reference each other

## Daily Notes Context

Daily notes serve multiple purposes:
- **Work tracking**: Record what was accomplished
- **Time analysis**: Capture time spent and patterns
- **Knowledge growth**: Document learning and insights
- **People interactions**: Track collaboration and relationships
- **Reflection**: Identify what worked well and what didn't
- **Planning**: Set priorities for tomorrow/next week

### Daily Note Structure
```markdown
# Daily Closeout - [Date]

## Work Completed
- [Work description] - [duration] ([work_type])

## Time Summary
- Total productive time: X hours Y minutes
- By work type: [breakdown]
- Distractions: X minutes

## Knowledge & People
- Knowledge created/updated: [[Topic 1]], [[Topic 2]]
- People interactions: [[Person 1]], [[Person 2]]

## Reflections
- What went well:
- What took longer than expected:
- What I learned:
- Blockers or challenges:

## Tomorrow's Focus
- [Priority items for next day]
```

## Interaction Style

- Be direct, friendly, and concise
- Batch follow-up questions when processing backlog
- Always tie tasks to goals in the Context section
- Process backlog items ONE AT A TIME interactively
- Suggest no more than 3 focus tasks for daily work
- Use Obsidian [[links]] format for all cross-references
