---
inclusion: always
---

# WorkOS Reference Guide

## Time Estimation Guidance

### The Math of Focus and Interruptions

Time estimates must account for three parameters:

1. **λ (lambda)** - Interruption rate (interruptions per hour)
   - Typical knowledge worker: 2-3 per hour
   - Heavy collaborator/manager: 15-30 per hour
   - Protected focus time: 0-1 per hour

2. **Δ (delta)** - Recovery time after interruption (minutes)
   - Research shows: 10-16 minutes to resume work after email/IM
   - Minimum: 10 minutes (with good breadcrumbs)
   - Typical: 15-20 minutes
   - Complex work: 20-25 minutes

3. **θ (theta)** - Minimum uninterrupted time for meaningful work (minutes)
   - Deep work (coding, writing, analysis): 60-90 minutes
   - Medium work (reviews, planning): 30-45 minutes
   - Light work (admin, email): 15-30 minutes

### Estimation Framework

**Step 1:** Estimate Pure Work Time (zero interruptions)

**Step 2:** Identify Work Type (θ)
- **Deep work** (θ=60-90): Writing, coding, complex analysis, strategy
- **Medium work** (θ=30-45): Reviews, planning, design iterations
- **Light work** (θ=15-30): Admin, email, quick responses

**Step 3:** Assess Environment (λ)
- **Protected time** (λ=0-1): Early morning, blocked calendar, off-hours
- **Normal day** (λ=2-3): Typical work hours with some meetings
- **High interrupt** (λ=4+): Back-to-back meetings, on-call, reactive work

**Step 4:** Calculate Realistic Time
```
Realistic Time = Pure Work Time × Multiplier
```

**Multipliers by environment:**
- Protected time (λ=0-1): 1.0-1.2x
- Normal day (λ=2-3): 1.5-2.0x
- High interrupt (λ=4+): 2.5-3.0x or break into smaller tasks

**Step 5:** Match Task to Environment
- If multiplier > 2.0x, consider breaking into smaller chunks or reserving for protected time

### Practical Guidelines

**Data work:** Add 50-100% buffer (consistently underestimated)
**Writing work:** Requires θ=60-90 minutes, estimate 2x in normal environment
**Review work:** Can work with θ=30 minutes, estimate 1.5x
**Iterative work:** Estimate per iteration, not total

## Work Type Taxonomy

Tasks can be tagged with a `work_type` field:

### deep
Uninterrupted focus work requiring sustained concentration.
- Examples: Writing documents, coding, complex analysis, strategy development
- Scheduling: Needs 2-4 hour blocks, morning preferred
- Energy: High cognitive load

### review
Evaluating others' work and providing feedback.
- Examples: Document reviews, code reviews, feedback on proposals
- Scheduling: Can do in 30-60 min chunks, afternoon OK
- Energy: Medium cognitive load

### reactive
On-demand responses to others' requests.
- Examples: Slack responses, email, ad-hoc questions, WBR follow-up
- Scheduling: Unpredictable timing, hard to estimate
- Energy: Variable, often interruptive

### iterative
Work requiring multiple short sessions over time with feedback loops.
- Examples: Document revisions, design iterations, ongoing refinements
- Scheduling: Spread across days, total time misleading
- Energy: Medium, but requires context switching

### collaborative
Real-time work with others.
- Examples: Meetings, pairing sessions, workshops, brainstorming
- Scheduling: Scheduled, but prep time needed before
- Energy: High social energy required

### research
Exploratory, learning-oriented work.
- Examples: Reading documentation, investigating options, learning new tools
- Scheduling: Flexible timing, can pause/resume easily
- Energy: Medium, curiosity-driven

### admin
Routine operational tasks.
- Examples: Expense reports, scheduling, task management, email cleanup
- Scheduling: Low energy, end of day fine
- Energy: Low cognitive load

## Git Workflow

### What to Commit
Always include these directories and files in commits:
- Local operational files: Tasks/, GOALS.md, .kiro/, config.yaml
- Note: Knowledge files are now in consolidated knowledgebase (knowledgebase/-common/)

### Commit Command
```bash
git add Tasks/ GOALS.md .kiro/ config.yaml
git commit -m "Update tasks - [current date]"
```

### When to Commit
- Processing backlog and creating new tasks
- Completing or updating multiple tasks
- Making significant changes to GOALS.md
- Adding new Topics files
- Weekly reviews
- End of work session

### What NOT to Commit
These are gitignored:
- `BACKLOG.md` - Personal inbox
- `knowledgebase/-common/Daily/` - Private reflections
- `.system/session_tracker.json` - Session state
- `knowledgebase/-common/People/*.md` - Personal contact information
- Personal task files with sensitive information

### Important Notes
- **User does NOT push to GitHub** - Commits stay local
- **No need to push** - This is a local-only workflow
- Focus on local commit history for tracking changes

## Best Practices

### Time-of-Day Matching
- **Morning:** Deep work (θ=60-90 min blocks)
- **Afternoon:** Review and collaborative work
- **End of day:** Admin tasks

### Energy Management
- Don't schedule all deep work back-to-back
- Balance reactive/collaborative with focused work
- Reserve protected time for high-θ work

### Workload Balance
- Identify when overloaded with reactive/collaborative work
- Use work_type to assess daily balance
- Adjust priorities based on available time blocks
