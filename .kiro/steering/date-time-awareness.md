---
inclusion: always
---

# Date and Time Awareness

## Current Date Context

**IMPORTANT**: Always verify the current date before making date-based decisions.

The system prompt includes a `<current_date_and_time>` section, but it may be stale in long conversations.

## How to Get Current Date

Use bash command to get fresh date:
```bash
date +"%Y-%m-%d"
```

Use bash command to get day of week:
```bash
date +"%A"
```

Use bash command to get full timestamp:
```bash
date
```

## When to Check Current Date

**Always check current date when:**
- Starting morning routine ("start my day", "good morning")
- Running daily closeout ("close out today")
- Running weekly closeout ("close out this week")
- Checking if closeouts are missing
- Creating dated files (daily-notes/YYYY-MM-DD.md)
- Determining if it's Monday (for weekly checks)
- Calculating "yesterday" or "last week"

## Date Calculations

**Yesterday:**
```bash
date -v-1d +"%Y-%m-%d"
```

**Last Monday (start of last week):**
```bash
date -v-Mon -v-7d +"%Y-%m-%d"
```

**This Monday (start of this week):**
```bash
date -v-Mon +"%Y-%m-%d"
```

**Last Friday:**
```bash
date -v-Fri -v-7d +"%Y-%m-%d"
```

## Session Tracker Date Fields

Always update these fields with current dates:
- `day`: Current date (YYYY-MM-DD)
- `current_week_start`: Monday of current week (YYYY-MM-DD)
- `last_daily_closeout`: Date of last completed daily closeout
- `last_weekly_closeout`: Date of last completed weekly closeout

## Best Practices

1. **Start every date-sensitive workflow** by running `date` command
2. **Store the result** in a variable for the workflow
3. **Use ISO format** (YYYY-MM-DD) for consistency
4. **Update session tracker** with current date when starting work
5. **Don't rely on system prompt date** - always check fresh

## Example Workflow Start

```bash
# Get current date
TODAY=$(date +"%Y-%m-%d")
DAY_OF_WEEK=$(date +"%A")
THIS_MONDAY=$(date -v-Mon +"%Y-%m-%d")

# Now use these variables for logic
echo "Today is $DAY_OF_WEEK, $TODAY"
echo "This week started on $THIS_MONDAY"
```

## Closeout Date Logic

**For daily closeout:**
- Get today's date
- Check if today's date > last_daily_closeout
- If yes, closeout is missing

**For weekly closeout:**
- Get today's date and day of week
- If Monday, check if last_weekly_closeout < last Friday
- If yes, weekly closeout is missing

**For morning startup:**
- Get today's date and day of week
- Check yesterday's closeout (today - 1 day)
- If Monday, also check last week's closeout
