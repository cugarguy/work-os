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

## Important
- Always use the MCP tools (don't just read files manually)
- Keep responses concise and actionable
- Tie everything back to GOALS.md
- Check for missing closeouts every morning before starting work
