---
inclusion: fileMatch
fileMatchPattern: "Knowledge/*.md"
---

# Knowledge Base Context

When working with files in the Knowledge/ directory:

## Purpose

Knowledge/ stores:
- Reference documentation and specs
- Meeting notes (non-personal)
- Research findings and analysis
- Process documentation
- Project briefs and requirements
- Technical documentation
- Best practices and guidelines

## File Naming

Use descriptive, kebab-case names:
- `wbr-review-2025-11-14.md`
- `unified-platform-notes.md`
- `productivity-tools.md`
- `q-ai-best-practices.md`

## Integration with Tasks

- Reference Knowledge files in task `resource_refs` field
- Link from task Context sections to provide background
- Create Knowledge files for complex task context
- Use Knowledge files to avoid duplicating information across tasks

## Best Practices

1. **Make it reusable** - Write for future reference, not just current context
2. **Link from tasks** - Always reference relevant Knowledge files in task resource_refs
3. **Keep it updated** - Update existing files rather than creating duplicates
4. **Use clear titles** - File names should indicate content at a glance
5. **Add dates for time-sensitive content** - Include dates in filename or frontmatter

## When to Create Knowledge Files

Create a new Knowledge file when:
- Multiple tasks reference the same context
- You have meeting notes that inform ongoing work
- You're documenting a process or system
- You have research findings to preserve
- You need to store specs or requirements

## When to Update vs Create New

**Update existing file when:**
- Adding to ongoing project notes
- Updating process documentation
- Adding new findings to research
- Continuing a topic or theme

**Create new file when:**
- Starting a completely new topic
- Documenting a new meeting or event
- Different time period or context
- Separate project or initiative

## Structure Suggestions

For meeting notes:
```markdown
# Meeting: [Topic] - [Date]

## Attendees
## Agenda
## Discussion
## Decisions
## Action Items
```

For process documentation:
```markdown
# [Process Name]

## Overview
## Steps
## Tools/Resources
## Tips & Best Practices
```

For research:
```markdown
# [Research Topic]

## Context
## Findings
## Sources
## Implications
```
