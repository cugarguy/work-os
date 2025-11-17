---
inclusion: always
---

# Daily & Weekly Closeout Workflows

## Morning Startup Check

Every morning when starting work:
1. Check if previous day was closed out
2. If not closed out → Run daily closeout for previous day FIRST
3. Then start current day

Every Monday morning:
1. Check if previous week was closed out
2. If not closed out → Run weekly closeout for previous week FIRST
3. Then start current week

## Daily Closeout Workflow

Trigger phrases: "close out today", "end of day", "daily closeout"

**Steps:**
1. Use `list_tasks` with `include_done=true` to see all tasks
2. Identify tasks completed today (status='d', check Progress Log for today's date)
3. For each completed task, gather:
   - Task title and priority
   - Estimated time vs actual time (if tracked)
   - What was accomplished
4. Identify tasks worked on but not completed (status='s')
5. Ask about:
   - Total productive time today
   - Any distractions or unplanned work
   - Blockers encountered
   - What went well / what didn't
6. Create summary in `daily-notes/YYYY-MM-DD.md`:
   ```markdown
   # Daily Closeout - [Date]
   
   ## Completed Tasks
   - [P0] Task name - [time spent]
   - [P1] Task name - [time spent]
   
   ## In Progress
   - Task name - current status
   
   ## Time Summary
   - Productive time: X hours
   - Distractions: Y hours (description)
   - Unplanned work: Z hours (description)
   
   ## Reflections
   - What went well:
   - What didn't:
   - Blockers:
   
   ## Tomorrow's Focus
   - Top 3 priorities for tomorrow
   ```
7. Update session tracker with closeout completion
8. Suggest top 3 priorities for tomorrow based on P0/P1 tasks

## Weekly Closeout Workflow

Trigger phrases: "close out this week", "weekly closeout", "end of week"

**Steps:**
1. Use `list_tasks` with `include_done=true` to see all tasks
2. Identify tasks completed this week (check Progress Log for this week's dates)
3. For each completed task, gather:
   - Task title, priority, category
   - Time spent
   - Goal alignment (from Context section)
4. Identify tasks started but not completed
5. Ask about:
   - Total productive time this week
   - Major accomplishments
   - Distractions and time sinks
   - Blockers that need addressing
   - Goals progress
6. Create summary in `daily-notes/weekly-closeout-YYYY-MM-DD.md`:
   ```markdown
   # Weekly Closeout - Week of [Date]
   
   ## Completed Tasks by Priority
   ### P0 (Critical)
   - Task name - [time] - Goal: [goal reference]
   
   ### P1 (Important)
   - Task name - [time] - Goal: [goal reference]
   
   ### P2/P3
   - Task name - [time]
   
   ## In Progress
   - Task name - current status and blockers
   
   ## Time Summary
   - Total productive time: X hours
   - Average per day: Y hours
   - Distractions: Z hours (patterns)
   
   ## Goal Progress
   - [Goal 1]: Progress made this week
   - [Goal 2]: Progress made this week
   
   ## Reflections
   - Major wins:
   - Challenges:
   - Blockers to address:
   - Patterns noticed:
   
   ## Next Week's Focus
   - Top 3-5 priorities
   - Goals to advance
   - Blockers to remove
   ```
7. Use `check_priority_limits` to see if overloaded
8. Use `prune_completed_tasks` to clean up old tasks (optional)
9. Update session tracker with weekly closeout completion
10. Suggest priorities for next week

## Session Tracker Updates

The session tracker (`.system/session_tracker.json`) should track:
- `last_daily_closeout`: Date of last daily closeout (YYYY-MM-DD)
- `last_weekly_closeout`: Date of last weekly closeout (YYYY-MM-DD)
- `current_week_start`: Monday of current week (YYYY-MM-DD)

## Closeout Completion Criteria

**Daily closeout is complete when:**
- Summary created in daily-notes/
- All completed tasks reviewed
- Time tracked
- Tomorrow's priorities identified
- Session tracker updated

**Weekly closeout is complete when:**
- Summary created in daily-notes/
- All week's completed tasks reviewed
- Goal progress assessed
- Next week's priorities identified
- Session tracker updated

## Integration with Existing Workflows

- Daily closeout feeds into "what should I work on" for next day
- Weekly closeout informs weekly review and goal updates
- Closeout data helps with time estimates for future tasks
- Distraction tracking improves productivity insights
