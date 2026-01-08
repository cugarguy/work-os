---
inclusion: always
---

# WorkOS Workflows

## Morning Startup Workflow

**Trigger phrases:** "start my day", "good morning", "begin work"

**Steps:**
1. **Get current date first**: Run `date +"%Y-%m-%d"`, `date +"%A"`, and `date +"%Y-%m"`
2. Read session tracker
3. **Check for monthly startup**: Compare current month to last_monthly_startup month
   - If different month → Run monthly startup FIRST
4. **Check for weekly startup**: If Monday or Tuesday AND last_weekly_startup < this Monday
   - Calculate this Monday: `date -v-Mon +"%Y-%m-%d"`
   - If last_weekly_startup before this Monday → Run weekly startup
5. **Check for missing daily closeout**: Calculate yesterday's date
   - If yesterday not closed out → Run daily closeout for yesterday FIRST
6. **Check for missing weekly closeout**: If Monday/Tuesday, check last Friday
   - Calculate last Friday: `date -v-Fri -v-7d +"%Y-%m-%d"`
   - If previous week not closed out → Run weekly closeout FIRST
7. **Check backlog**: Read BACKLOG.md
   - If backlog has items → Run backlog processing workflow
   - Process items ONE AT A TIME
   - Clear backlog before continuing
8. Then show today's priorities (P0/P1 tasks)
9. Suggest 1-3 focus tasks for today
10. Update session tracker with current day and week start

## Daily Check-In Workflow

**Purpose:** Capture work that happened when you weren't actively using the agent.

**When to run:**
- Time gap > 4 hours since last interaction
- Previous day(s) not closed out
- Session tracker shows work may have happened

**Steps:**
1. **Assess time gap** - Calculate time since last interaction
2. **Identify missing days** - Check for days without closeouts
3. **Interactive questions** (ONE at a time):
   - "Did you work on [date]?"
   - "What work did you do on [date]?"
   - For each work item: duration, type, knowledge areas, people involved
   - "Any distractions or interruptions?"
   - "What did you learn or create?"
   - "Anything blocking you or noteworthy?"
4. **Create time entries** for each work item
5. **Update knowledge & people** based on responses
6. **Create retroactive daily note** in `knowledgebase/-common/Daily/YYYY-MM-DD.md`
7. **Update session tracker**
8. **Provide summary** of what was captured

## Daily Closeout Workflow

**Trigger phrases:** "close out today", "end of day", "daily closeout"

**Interaction Style:** Ask ONE question at a time, wait for response

**Steps:**
1. **Process notes inbox FIRST**: Check if NOTES_INBOX.md has items
2. **Review today's time entries**: Use `get_time_history` with `days=1`
3. **Review knowledge and people updates**
4. **Gather reflections**:
   - What work took longer than expected? Why?
   - What work went faster than expected? Why?
   - Any distractions or interruptions?
   - What did you learn today?
   - Any blockers or challenges?
5. **Create summary** in `knowledgebase/-common/Daily/YYYY-MM-DD.md`
6. **Update session tracker** with closeout completion date
7. **Suggest tomorrow's focus**

## Weekly Closeout Workflow

**Trigger phrases:** "close out this week", "weekly closeout", "end of week"

**Steps:**
1. **Review week's time entries**: Use `get_time_history` with `days=7`
2. **Analyze patterns**: Use analysis tools
   - `get_distraction_analysis` with `days=7`
   - `get_expertise_analysis`
   - `get_collaboration_analysis` with `days=7`
   - `get_time_trends`
3. **Review knowledge growth**
4. **Review people interactions**
5. **Gather reflections**
6. **Create summary** in `knowledgebase/-common/Daily/weekly-closeout-YYYY-MM-DD.md`
7. **Update session tracker**
8. **Suggest next week's focus**

## Weekly Startup Workflow

**Trigger phrases:** "start the week", "weekly startup", "begin the week"
**When to run:** Every Monday morning (or first work day of week)

**Steps:**
1. Check if previous week was closed out
2. If not closed out → Run weekly closeout FIRST
3. Review project progress across active parent tasks
4. Highlight projects falling behind schedule
5. Suggest priority adjustments if needed
6. Show this week's focus areas
7. Update session tracker with week start

## Monthly Startup Workflow

**Trigger phrases:** "start the month", "monthly startup", "begin the month", "new month review"
**When to run:** First work day of each new month

**Steps:**
1. Check if previous month's last week was closed out
2. If not → Run weekly closeout FIRST
3. Review previous month (completed tasks, time, patterns)
4. Review outstanding initiatives (all P0/P1 parent tasks)
5. Review GOALS.md and assess progress
6. Plan for the month (must complete, focus areas, adjustments)
7. Update session tracker with month start

## Meeting Notes Workflow

### During Meeting
1. **Create meeting file** in Topics/ folder: `[Topic]-Meeting-YYYY-MM-DD.md`
2. **Capture notes in real-time**
3. **Link people mentioned**

### After Meeting
1. **Create tasks from action items**
2. **Update person files**
3. **Link to projects**
4. **Update related tasks**

### Natural Meeting Capture
**Trigger phrases:** "in a meeting", "attending [meeting]", "meeting for [topic]"
**End phrases:** "meeting is over", "meeting ended", "finished the meeting"

**Process:**
1. Ask for meeting topic (if not clear)
2. Create meeting notes file in Topics/
3. Enter note-taking mode
4. When meeting ends, automatically process action items

### Meeting Notes Template
```markdown
# [Meeting Topic] - [Date]

## Meeting Info
- **Date:** YYYY-MM-DD
- **Topic:** [Meeting purpose]
- **Attendees:** 
  - [Name] ([role/context])

## Notes
### [Topic 1]
- Key points
- Decisions made

## Action Items
- [ ] [Action item with owner]

## Follow-up
- [Any follow-up needed]

## Related
- [[Project: Name]]
- [[Person Name]]
- [[Task Name]]
```

## Backlog Processing Workflow

**Trigger phrases:** "triage backlog", "process backlog", "clear backlog"

**Steps:**
1. Read BACKLOG.md, GOALS.md, and consolidated knowledgebase files
2. Extract actionable items from backlog
3. Use process_backlog_with_dedup to check for duplicates
4. Process items ONE AT A TIME interactively
5. Ask questions about category, priority, details as needed
6. Create tasks with full Context sections tied to GOALS.md
7. Clear backlog when done

## Task Management Workflows

### Task Completion
**Trigger phrases:** "mark done", "complete task", "finish task"
1. Use list_tasks to show active tasks
2. Ask which task to mark as done
3. Use update_task_status to mark it 'd'
4. Confirm and show remaining P0/P1 tasks

### Priority Review
**Trigger phrases:** "review backlog", "prioritize tasks", "review priorities"
1. Read GOALS.md to understand current objectives
2. Use list_tasks to get all active tasks
3. Review each task ONE AT A TIME for goal alignment and priority
4. Update task priorities as needed
5. Summarize final priority distribution

### Weekly Review
**Trigger phrases:** "weekly review", "what did I accomplish", "clean up old tasks"
1. Use list_tasks with include_done=true
2. Summarize accomplishments tied to goals
3. Use get_task_summary for current workload
4. Use check_priority_limits to check if overloaded
5. Ask about pruning old completed tasks
6. Suggest goals needing attention

## People Management Workflows

### Add Person
**Trigger phrases:** "add person", "create person file"
1. Ask for person's name
2. Ask for role/title and team/organization
3. Ask about relationship context
4. Ask about key projects/topics you work on together
5. Create person file from template in People/[Name].md
6. Use Obsidian [[links]] format for cross-references

### Update Person Notes
**Trigger phrases:** "update person notes", "add notes for [person]"
1. Find person file or offer to create it
2. Ask for note type: meeting, conversation, email, or general
3. Ask for key discussion points and action items
4. Add dated entry to person's file
5. Auto-link mentioned tasks and knowledge docs
6. Update person file's "Last Updated" date

### Link Person to Task
**Trigger phrases:** "link person to task", "connect [person] to [task]"
1. Verify person file exists (create if needed)
2. Verify task file exists
3. Add person to task's resource_refs: People/[Name].md
4. Add task to person's "Related Tasks/Projects" section
5. Confirm bidirectional link created

## Date and Time Awareness

**IMPORTANT:** Always verify current date before making date-based decisions.

### When to Check Current Date
- Starting morning/daily routines
- Running closeouts (daily, weekly, monthly)
- Creating dated files
- Determining if closeouts are missing
- Calculating "yesterday", "last week", etc.

### How to Get Current Date
```bash
date +"%Y-%m-%d"        # Current date
date +"%A"              # Day of week
date                    # Full timestamp
date -v-1d +"%Y-%m-%d"  # Yesterday
date -v-Mon +"%Y-%m-%d" # This Monday
```

**Best Practice:** Start every date-sensitive workflow by running `date` command.

## Session Tracker Updates

The session tracker (`.system/session_tracker.json`) should track:
- `last_daily_closeout`: Date of last daily closeout (YYYY-MM-DD)
- `last_weekly_closeout`: Date of last weekly closeout (YYYY-MM-DD)
- `last_monthly_startup`: Date of last monthly startup (YYYY-MM-DD)
- `current_week_start`: Monday of current week (YYYY-MM-DD)

## Integration Points

- Daily closeout captures time data for analysis
- Weekly closeout provides pattern insights
- Closeout data improves time estimates
- All workflows tie back to GOALS.md
- Use Obsidian [[links]] format for all cross-references
- Always use MCP tools (don't read files manually)
