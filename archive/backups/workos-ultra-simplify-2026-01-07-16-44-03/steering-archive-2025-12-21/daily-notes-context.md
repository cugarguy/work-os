---
inclusion: fileMatch
fileMatchPattern: "daily-notes/*.md"
---

# Daily Notes Context

When working with daily notes in the daily-notes/ directory:

## Naming Convention

Use ISO date format: `YYYY-MM-DD.md`

Example: `2025-11-14.md`

## Purpose

Daily notes are for:
- Time-stamped reflections and observations
- Daily journals and work logs
- Quick captures that don't fit elsewhere
- End-of-day summaries
- Personal notes and thoughts

## Distinction from Other Directories

- **Tasks/** - Structured, actionable tasks with priorities and status
- **Knowledge/** - Reference material, documentation, meeting notes
- **BACKLOG.md** - Unprocessed inbox items waiting to be triaged
- **daily-notes/** - Personal daily reflections and journals

## Best Practices

1. **One file per day** - Keep daily notes consolidated
2. **Timestamp entries** - Use time stamps for multiple entries in one day
3. **Link to tasks** - Reference Tasks/ files when relevant
4. **Don't duplicate** - If something becomes actionable, move it to BACKLOG.md
5. **Keep it personal** - These are your private reflections

## Privacy Note

Daily notes are gitignored by default to keep personal reflections private.

## When to Use Daily Notes vs Other Locations

- **Actionable item** → BACKLOG.md (to be processed into Tasks/)
- **Reference material** → Knowledge/
- **Meeting notes with stakeholders** → People/ or Knowledge/
- **Personal reflection** → daily-notes/
- **Quick thought or observation** → daily-notes/
