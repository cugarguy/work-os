---
inclusion: always
---

# Work Type Taxonomy

## Work Types

Tasks can be tagged with a `work_type` field to indicate the attention pattern and scheduling needs:

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

## Usage in Task Management

Add to task frontmatter:
```yaml
work_type: deep  # or review, reactive, iterative, collaborative, research, admin
```

## Benefits

- **Time-of-day matching**: Suggest deep work in morning, admin in afternoon
- **Energy management**: Don't schedule all deep work back-to-back
- **Realistic estimation**: Reactive work is unpredictable, iterative spreads over days
- **Workload balance**: Identify when overloaded with reactive/collaborative work
- **Calendar blocking**: Know when you need uninterrupted time blocks

## Default Mappings

If work_type not specified, infer from category:
- technical → deep
- writing → deep
- research → research
- outreach → collaborative
- admin → admin
- personal → varies
