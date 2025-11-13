---
inclusion: always
---

# PersonalOS Chat Commands

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

## "show priorities" or "what's urgent" or "p0 tasks"
Execute the priority view workflow:
1. Use list_tasks with priority=P0,P1
2. Group by priority
3. Show estimated time for each level
4. Keep it concise

## "weekly review" or "what did I accomplish"
Execute the weekly review workflow:
1. Use list_tasks with include_done=true
2. Summarize accomplishments tied to goals
3. Use get_task_summary for current workload
4. Use check_priority_limits to check if overloaded
5. Ask about pruning old completed tasks
6. Suggest goals needing attention

## Important
- Always use the MCP tools (don't just read files manually)
- Keep responses concise and actionable
- Tie everything back to GOALS.md
