---
inclusion: always
---

# WorkOS Chat Commands

When the user says certain phrases in chat, execute the corresponding workflow:

## "triage backlog" or "process backlog" or "clear backlog"
Execute the backlog processing workflow:
1. Read #BACKLOG.md, #GOALS.md, #Tasks/, #Knowledge/
2. Extract actionable items from backlog
3. Use process_backlog_with_dedup to check for duplicates
4. Process items ONE AT A TIME interactively
5. Ask questions about category, priority, details as needed
6. Create tasks with full Context sections tied to GOALS.md
7. Clear backlog when done

## "process capture" or "triage capture" or "clear capture"
Execute the capture processing workflow:
1. Read #CAPTURE.md, #GOALS.md, #Tasks/, #Knowledge/
2. Extract items from capture file
3. For each item, ask: Task, Knowledge, Goal update, Skip, or Delete?
4. If Task: use process_backlog_with_dedup, create with full Context
5. If Knowledge: ask for filename, save to Knowledge/
6. If Goal: ask which section to update in GOALS.md
7. If Skip: leave in CAPTURE.md, move to next
8. If Delete: remove from CAPTURE.md
9. Process ONE AT A TIME interactively
10. Only remove processed items (not skipped ones)

## "what should I work on" or "daily focus" or "review my day"
Execute the daily focus workflow:
1. Read #GOALS.md and #Tasks/
2. Use list_tasks to show P0 and P1 tasks
3. Consider quarterly objectives from GOALS.md
4. Suggest 1-3 tasks to focus on today
5. Explain why each matters for goals
6. Flag any blocked tasks

## "mark done" or "complete task" or "finish task"
Execute the task completion workflow:
1. Use list_tasks to show active tasks
2. Ask which task to mark as done
3. Use update_task_status to mark it 'd'
4. Confirm and show remaining P0/P1 tasks

## "show priorities" or "what's urgent" or "p0 tasks" or "show me today's priorities"
Execute the priority view workflow:
1. Use list_tasks with priority=P0,P1
2. Group by priority
3. Show estimated time for each level
4. Keep it concise

## "weekly review" or "what did I accomplish" or "clean up old tasks"
Execute the weekly review workflow:
1. Use list_tasks with include_done=true
2. Summarize accomplishments tied to goals
3. Use get_task_summary for current workload
4. Use check_priority_limits to check if overloaded
5. Ask about pruning old completed tasks (use prune_completed_tasks)
6. Suggest goals needing attention

## "review backlog" or "prioritize tasks" or "review priorities"
Execute the task prioritization workflow:
1. Read #GOALS.md to understand current objectives and deadlines
2. Use list_tasks to get all active tasks (not done)
3. Group tasks by current priority (P0, P1, P2, P3)
4. For each task, review ONE AT A TIME:
   - Does it still align with current goals?
   - Is the priority still correct given deadlines?
   - Should it move up (more urgent) or down (less urgent)?
   - Consider work_type for scheduling feasibility
5. Ask user to confirm priority changes
6. Update task priorities as needed
7. Summarize final priority distribution

## "show blocked tasks" or "what's blocked"
Execute the blocked tasks workflow:
1. Use list_tasks with status=b
2. Show blocked tasks with their context
3. Ask what's blocking each one
4. Suggest next steps to unblock

## "tasks for goal" or "show tasks supporting [goal]"
Execute the goal-aligned tasks workflow:
1. Read GOALS.md to understand the goal
2. Use list_tasks to get all active tasks
3. Filter tasks that reference this goal in Context
4. Show how these tasks advance the goal

## "backup tasks" or "backup my tasks"
Execute the backup workflow:
1. Create backups/tasks-[YYYY-MM-DD-HH-MM]/ directory
2. Copy all files from Tasks/ to backup folder
3. Confirm backup created with file count
4. List the 5 most recent backups

## "commit to git" or "git commit" or "save to git"
Execute the git commit workflow:
1. Run: git add Tasks/ GOALS.md Knowledge/ .kiro/ config.yaml
2. Run: git commit -m "Update tasks - [current date]"
3. Confirm commit successful and show commit hash
4. Show recent commits

## "close out today" or "end of day" or "daily closeout"
Execute the daily closeout workflow:
1. **Get current date first**: Run `date +"%Y-%m-%d"`
2. Use list_tasks with include_done=true
3. Identify tasks completed today (check Progress Log for today's date)
4. Identify tasks in progress (status='s')
5. Ask about: productive time, distractions, blockers, reflections
6. Create summary in daily-notes/YYYY-MM-DD.md with:
   - Completed tasks with time spent
   - In progress tasks
   - Time summary (productive, distractions, unplanned)
   - Reflections (what went well, what didn't, blockers)
   - Tomorrow's top 3 priorities
7. Update session tracker: set last_daily_closeout to today's date
8. Suggest tomorrow's focus based on P0/P1 tasks

## "close out this week" or "weekly closeout" or "end of week"
Execute the weekly closeout workflow:
1. **Get current date first**: Run `date +"%Y-%m-%d"` and calculate week dates
2. Calculate this Monday: `date -v-Mon +"%Y-%m-%d"`
3. Use list_tasks with include_done=true
4. Identify tasks completed this week (check Progress Log for dates >= this Monday)
5. Group by priority and link to goals
6. Ask about: total time, major accomplishments, distractions, goal progress
7. Create summary in daily-notes/weekly-closeout-YYYY-MM-DD.md with:
   - Completed tasks by priority with goal alignment
   - In progress tasks with blockers
   - Time summary and patterns
   - Goal progress assessment
   - Reflections and wins
   - Next week's priorities
8. Use check_priority_limits to assess workload
9. Optionally use prune_completed_tasks
10. Update session tracker: set last_weekly_closeout to today's date
11. Suggest next week's focus

## "start my day" or "good morning" or "begin work"
Execute the morning startup workflow:
1. **Get current date first**: Run `date +"%Y-%m-%d"` and `date +"%A"`
2. Read session tracker for last_daily_closeout
3. Calculate yesterday's date: `date -v-1d +"%Y-%m-%d"`
4. If yesterday not closed out → Run daily closeout for yesterday FIRST
5. If today is Monday, check last_weekly_closeout
6. Calculate last Friday: `date -v-Fri -v-7d +"%Y-%m-%d"`
7. If previous week not closed out → Run weekly closeout FIRST
8. Then show today's priorities (P0/P1 tasks)
9. Suggest 1-3 focus tasks for today
10. Update session tracker with current day and week start

## "add person" or "create person file"
Execute the add person workflow:
1. Ask for person's name
2. Ask for role/title and team/organization
3. Ask about relationship context (how you know them, working relationship)
4. Ask about key projects/topics you work on together
5. Create person file from template in People/[Name].md
6. Use Obsidian [[links]] format for cross-references
7. Confirm file created

## "update person notes" or "add notes for [person]"
Execute the person notes workflow:
1. If person name provided, find their file; otherwise ask for name
2. If person file doesn't exist, offer to create it
3. Ask for note type: meeting, conversation, email, or general
4. Ask for key discussion points
5. Ask for action items (if any)
6. Add dated entry to person's file
7. Auto-link any mentioned tasks using [[Task Name]] format
8. Auto-link any mentioned knowledge docs using [[Doc Name]] format
9. Update person file's "Last Updated" date
10. Confirm notes added

## "link person to task" or "connect [person] to [task]"
Execute the bidirectional linking workflow:
1. If person/task not specified, ask for both
2. Verify person file exists (create if needed)
3. Verify task file exists
4. Add person to task's resource_refs: People/[Name].md
5. Add task to person's "Related Tasks/Projects" section using [[Task Name]]
6. Confirm bidirectional link created

## "update other people" or "review other people"
Execute the Other People file update workflow:
1. Read People/Other People.md
2. Check if any person has been mentioned 3+ times across files
3. If yes, suggest promoting them to their own person file
4. Create dedicated file with context from Other People.md
5. Remove from Other People.md
6. Update any references to point to new file

## Meeting Notes - Natural Conversation
When user indicates they're in a meeting (phrases like "in a meeting", "attending [meeting]", "meeting for [topic]"):
1. Ask for meeting topic if not clear from context
2. Create meeting notes file: Knowledge/[Topic]-Meeting-YYYY-MM-DD.md
3. Enter note-taking mode - capture everything user shares
4. When user indicates meeting is over, automatically process:
   - Extract action items
   - Ask: Create tasks? Update person files? Link to projects?
   - Process responses and confirm completion
5. If ever unclear about meeting status, ask for clarification

## Important
- Always use the MCP tools (don't just read files manually)
- Keep responses concise and actionable
- Tie everything back to GOALS.md
- Check for missing closeouts every morning before starting work
- Use Obsidian [[links]] format for all cross-references
- Auto-link people when mentioned in tasks or notes
