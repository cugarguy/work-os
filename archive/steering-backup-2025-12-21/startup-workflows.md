---
inclusion: always
---

# Weekly and Monthly Startup Workflows

## Weekly Startup Workflow

Trigger phrases: "start the week", "weekly startup", "begin the week"

**When to run:** Every Monday morning (or first work day of week)

**Steps:**
1. Check if previous week was closed out
2. If not closed out → Run weekly closeout FIRST
3. Review project progress across active parent tasks:
   - For each P0/P1 parent task with subtasks:
     - Show completed subtasks vs total
     - Calculate % complete
     - Check if on track for due date
     - Identify any blockers
4. Highlight projects falling behind schedule
5. Suggest priority adjustments if needed
6. Show this week's focus areas
7. Update session tracker with week start

**Output format:**
```markdown
# Weekly Startup - Week of [Date]

## Project Progress Review

### [Parent Task Name] (Due: [Date])
- Progress: X of Y subtasks complete (Z%)
- Status: On track / Behind / Ahead
- Blockers: [Any blockers]
- This week: [Subtasks to focus on]

### [Parent Task Name 2]
...

## This Week's Priorities
1. [Top priority]
2. [Second priority]
3. [Third priority]

## Adjustments Needed
- [Any priority or plan adjustments]
```

## Monthly Startup Workflow

Trigger phrases: "start the month", "monthly startup", "begin the month", "new month review"

**When to run:** First work day of each new month

**Steps:**
1. Check if previous month's last week was closed out
2. If not → Run weekly closeout FIRST
3. Review previous month:
   - List all tasks completed in previous month
   - Calculate total time spent by category
   - Identify patterns (what took longer than expected)
   - Note major accomplishments
4. Review outstanding initiatives:
   - Check all P0/P1 parent tasks
   - Assess progress on each
   - Identify stalled initiatives
   - Flag overdue items
5. Review GOALS.md:
   - Read current quarterly objectives
   - Assess progress on each goal
   - Check if goals need updating
   - Identify goals needing more attention
6. Plan for the month:
   - What needs to complete this month?
   - Any new priorities emerging?
   - Adjust task priorities if needed
   - Set monthly focus areas
7. Update session tracker with month start

**Output format:**
```markdown
# Monthly Startup - [Month Year]

## Previous Month Review ([Month])

### Completed Tasks
- [P0] Task name - [time]
- [P1] Task name - [time]
...

### Time Summary
- Total productive time: X hours
- By category:
  - Technical: X hours
  - Writing: X hours
  - Research: X hours
  ...

### Major Accomplishments
- [Accomplishment 1]
- [Accomplishment 2]

### Patterns Observed
- [Pattern 1]
- [Pattern 2]

## Outstanding Initiatives

### [Parent Task Name] (Due: [Date])
- Progress: X of Y subtasks (Z%)
- Status: On track / Behind / At risk
- Action needed: [What needs to happen]

## Goals Progress Review

### [Goal from GOALS.md]
- Progress: [Assessment]
- Tasks supporting this goal: [Count and status]
- Attention needed: [Yes/No and why]

### [Goal 2]
...

## This Month's Plan ([Month])

### Must Complete
- [Critical item 1]
- [Critical item 2]

### Focus Areas
- [Focus area 1]
- [Focus area 2]

### Priority Adjustments
- [Any changes to priorities]

### New Priorities
- [Any new items emerging]
```

## Integration with Existing Workflows

**Morning startup ("start my day"):**
1. Get current date and day of week
2. Check if new month started since last session:
   - Compare current month (YYYY-MM) to `last_monthly_startup` month
   - If different month → Run monthly startup FIRST
3. Check if it's Monday or Tuesday AND no weekly startup yet this week:
   - Check if `last_weekly_startup` < this Monday's date
   - If yes → Run weekly startup
4. Then proceed with daily startup

**Session tracker fields:**
- `last_weekly_startup`: Date of last weekly startup (YYYY-MM-DD)
- `last_monthly_startup`: Date of last monthly startup (YYYY-MM-DD)
- `current_month`: Current month (YYYY-MM)

**Trigger logic:**
- **Weekly startup**: Monday or Tuesday AND `last_weekly_startup` is before this week's Monday
- **Monthly startup**: Current month (YYYY-MM) is different from month in `last_monthly_startup`

## Best Practices

**Weekly startup:**
- Focus on project-level progress, not individual tasks
- Use parent tasks with subtasks as "projects"
- Keep it quick (10-15 minutes)
- Adjust priorities based on progress

**Monthly startup:**
- More comprehensive than weekly
- Tie back to GOALS.md explicitly
- Look for patterns and learnings
- Reset expectations for the month
- Update goals if needed

**Both:**
- Always check for missing closeouts first
- Update session tracker when complete
- Keep output concise and actionable
