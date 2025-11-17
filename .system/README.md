# System Directory

Internal system files used by WorkOS. These files are auto-generated and managed by the system.

## Files

- **session_tracker.json** - Tracks current session state, active tasks, and context for continuity across restarts
  - Includes daily/weekly closeout tracking
  - Monitors current day and week
  - Ensures closeouts are completed before starting new work
- **WorkOS.base** - Base configuration for workspace views

## Session Tracker Fields

- `last_updated`: Timestamp of last update
- `current_task`: What you're currently working on
- `status`: Current status (working, paused, completed, blocked)
- `notes`: Session notes or context
- `next_action`: What to do next
- `day`: Current day (YYYY-MM-DD)
- `session_active`: Whether session is active
- `last_daily_closeout`: Date of last daily closeout (YYYY-MM-DD)
- `last_weekly_closeout`: Date of last weekly closeout (YYYY-MM-DD)
- `current_week_start`: Monday of current week (YYYY-MM-DD)

## Note

These files are gitignored by default as they contain session-specific data.
