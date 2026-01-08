---
inclusion: always
---

# Git Workflow

## What to Commit

Always include these directories and files in commits:
- Local operational files: Tasks/, GOALS.md, .kiro/, config.yaml
- Note: Knowledge files are now in consolidated knowledgebase (knowledgebase/-common/)

## Commit Command

```bash
git add Tasks/ GOALS.md .kiro/ config.yaml
git commit -m "Update tasks - [current date]"
```

## When to Commit

Commit after:
- Processing backlog and creating new tasks
- Completing or updating multiple tasks
- Making significant changes to GOALS.md
- Adding new Topics files
- Weekly reviews
- End of work session

## Commit Message Format

Use descriptive messages:
- `"Update tasks - 2025-11-14"`
- `"Process backlog - created 5 new tasks"`
- `"Weekly review - completed 8 tasks"`
- `"Update goals and priorities"`

## Important Notes

- **User does NOT push to GitHub** - Commits stay local
- **No need to push** - This is a local-only workflow
- **Remote is configured** but not used for publishing
- Focus on local commit history for tracking changes

## Git Status Check

Before committing, check status:
```bash
git status
```

This shows what's changed and ready to commit.

## Viewing Recent Commits

To see recent commit history:
```bash
git log --format="%h %s" -5
```

## What NOT to Commit

These are gitignored (don't commit):
- `BACKLOG.md` - Personal inbox
- `knowledgebase/-common/Daily/` - Private reflections (now in consolidated store)
- `.system/session_tracker.json` - Session state
- `knowledgebase/-common/People/*.md` - Personal contact information (now in consolidated store)
- Personal task files with sensitive information
