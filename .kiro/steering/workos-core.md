---
inclusion: always
---

# WorkOS Core System

## System Overview
- **GOALS.md**: Strategic direction, quarterly objectives, priority framework
- **BACKLOG.md**: Inbox for unstructured notes and ideas
- **Consolidated Store**: Primary knowledge repository at `knowledgebase/-common/`
  - Tasks: `knowledgebase/-common/Tasks/`
  - Knowledge: `knowledgebase/-common/Topics/`
  - People: `knowledgebase/-common/People/`

## MCP Tools (8 Essential)
**Complex Business Logic (Use MCP)**:
- `list_tasks`, `get_task_summary`, `check_priority_limits`
- `create_task`, `create_knowledge`, `create_person`
- `search_knowledge`, `link_person_to_knowledge`

**Simple Operations (Direct File Access)**:
- Update task status → `strReplace` on YAML frontmatter
- Clear backlog → `fsWrite("BACKLOG.md", "all done!")`
- System status → Directory existence checks
- Update knowledge/people → `strReplace` or `fsAppend`

## Priority Framework
- **P0 (Active)**: Working on it now - in progress, blocking others, time-sensitive
- **P1 (Next Up)**: Queued next - advances quarterly objectives, critical needs
- **P2 (Scheduled/Operational)**: Recurring work - meetings, reviews, maintenance
- **P3 (Downtime)**: When available - learning, exploration, nice-to-have

## Task Categories
- **technical**: build, fix, configure
- **outreach**: communicate, meet
- **research**: learn, analyze
- **writing**: draft, document
- **admin**: operations, finance, logistics
- **personal**: health, routines
- **other**: everything else

## Task Structure
```yaml
---
title: [Actionable task name]
category: [technical|outreach|research|writing|admin|personal|other]
priority: [P0|P1|P2|P3]
status: n  # n=not_started, s=started, b=blocked, d=done, p=pending, q=question
work_type: [deep|review|reactive|iterative|collaborative|research|admin]
created_date: [YYYY-MM-DD]
estimated_time: [minutes]
resource_refs:
  - Topics/example.md
  - People/John Smith.md
---

# [Task name]

## Context
Tie to goals from GOALS.md. Reference specific sections.

**Related to:** [Larger initiative]
**Dependencies:** [What this depends on/blocks]
**Why now:** [Timing rationale]

## Next Actions
- [ ] First action
- [ ] Second action

## Progress Log
- YYYY-MM-DD: Updates, decisions, progress
```

## Task Statuses
- **n**: Ready to work on, no blockers
- **s**: Currently in progress  
- **b**: Waiting on external dependency
- **d**: Completed
- **p**: Waiting on decision/timing
- **q**: Need more information

## Best Practices
- **Always tie tasks to GOALS.md** - Every Context section must reference goals
- **Process backlog ONE AT A TIME** - Interactive, not batch
- **Use MCP for complex logic** - Direct file access for simple operations
- **Auto-link people** - Add to resource_refs and update person files
- **Estimate time realistically** - Account for interruptions and work type