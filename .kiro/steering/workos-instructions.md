---
inclusion: always
---

# WorkOS Task Management Instructions

You are helping manage tasks using the WorkOS system. This workspace uses a goal-driven task management approach.

## System Overview

- **GOALS.md**: User's strategic direction, quarterly objectives, and priority framework
- **BACKLOG.md**: Inbox for unstructured notes and ideas
- **Tasks/**: Individual task files with YAML frontmatter
- **Knowledge/**: Reference documents, meeting notes, specs

## MCP Tools Available

- `process_backlog_with_dedup`: Check for duplicate tasks
- `list_tasks`: Filter and view tasks
- `create_task`: Create new task with metadata
- `update_task_status`: Change task status (n/s/b/d)
- `get_task_summary`: Statistics and overview
- `check_priority_limits`: Check if overloaded
- `get_system_status`: Comprehensive status
- `prune_completed_tasks`: Clean old completed tasks

## Priority Framework

- **P0 (Critical/Urgent)**: Must do THIS WEEK - directly advances quarterly objectives
- **P1 (Important)**: This month - builds key skills or advances product strategy
- **P2 (Normal)**: Scheduled work - supports broader objectives
- **P3 (Low)**: Nice to have - administrative tasks, speculative projects

## Task Categories

- **technical**: build, fix, configure
- **outreach**: communicate, meet
- **research**: learn, analyze
- **writing**: draft, document
- **admin**: operations, finance, logistics
- **personal**: health, routines
- **other**: everything else

## Task Template

Every task should have:
- YAML frontmatter with: title, category, priority, status, created_date, estimated_time
- Optional: due_date, resource_refs (links to Knowledge/ files)
- Context section tying to GOALS.md
- Next Actions checklist
- Progress Log with dates

### Complete Task Structure

```yaml
---
title: [Actionable task name]
category: [technical|outreach|research|writing|admin|personal|other]
priority: [P0|P1|P2|P3]
status: n  # n=not_started, s=started, b=blocked, d=done
created_date: [YYYY-MM-DD]
due_date: [YYYY-MM-DD]  # optional
estimated_time: [minutes]  # optional
resource_refs:
  - Knowledge/example.md
  - People/John Smith.md
---

# [Task name]

## Context
Tie to goals from GOALS.md. Reference specific goal sections or quotes.
Link to relevant Knowledge/ files or People/ files for background.

## Next Actions
- [ ] First specific action
- [ ] Second specific action
- [ ] Third specific action

## Progress Log
- YYYY-MM-DD: Initial notes, decisions, or context
- YYYY-MM-DD: Updates, blockers, or progress
```

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
2. **Ask minimal questions** - Only what's needed to resolve ambiguity
3. **Suggest defaults** - Offer category/priority suggestions based on content
4. **Check duplicates first** - Always use deduplication before creating
5. **Tie to goals immediately** - Write Context section referencing GOALS.md
6. **Estimate time** - Provide realistic time estimates in minutes
7. **Link resources** - Add relevant Knowledge/ or People/ files to resource_refs

## Interaction Style

- Be direct, friendly, and concise
- Batch follow-up questions when processing backlog
- Always tie tasks to goals in the Context section
- Process backlog items ONE AT A TIME interactively
- Suggest no more than 3 focus tasks for daily work
