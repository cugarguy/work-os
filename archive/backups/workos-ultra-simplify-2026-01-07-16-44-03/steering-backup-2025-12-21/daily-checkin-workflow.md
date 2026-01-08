---
inclusion: always
---

# Daily Check-In Workflow

## Purpose

The daily check-in captures work that happened when you weren't actively using the agent. It helps maintain temporal continuity and ensures all work is tracked, even if you didn't log it in real-time.

## When to Run

**Automatically triggered during morning startup when:**
- Time has passed since last interaction (gap > 4 hours)
- Previous day(s) not closed out
- Session tracker shows work may have happened

**Manually triggered when user says:**
- "Check in"
- "Update my work log"
- "Catch up on what I did"
- "Log recent work"

## Check-In Workflow

### Step 1: Assess Time Gap

Calculate time since last interaction:
```
Last interaction: [date/time from session tracker]
Current time: [now]
Time gap: [duration]
```

If gap > 4 hours, proceed with check-in.

### Step 2: Identify Missing Days

Check for days without closeouts:
```
Last daily closeout: [date from session tracker]
Today: [current date]
Missing days: [list of dates]
```

For each missing day, run check-in process.

### Step 3: Interactive Check-In Questions

Ask ONE question at a time, wait for response:

**For each missing day:**

1. **"Did you work on [date]?"**
   - If no → Mark as non-work day, move to next
   - If yes → Continue with questions

2. **"What work did you do on [date]?"**
   - Capture: Work descriptions (can be multiple items)
   - Example: "Worked on API design, had meeting with John, wrote documentation"

3. **For each work item, ask:**
   - "How long did this take?" (get duration in hours/minutes)
   - "What type of work was this?" (technical, writing, research, meeting, etc.)
   - "Any knowledge areas involved?" (suggest based on description)
   - "Any people involved?" (suggest based on description)

4. **"Any distractions or interruptions?"**
   - If yes: "What type and how long?"
   - Capture distraction data

5. **"What did you learn or create?"**
   - New knowledge to capture?
   - New people to add?
   - New connections to make?

6. **"Anything blocking you or noteworthy?"**
   - Capture blockers, challenges, insights

### Step 4: Create Time Entries

For each work item captured:
- Create time entry with:
  - Description
  - Duration
  - Work type
  - Knowledge references
  - People references
  - Distraction data (if any)
- Link to knowledge areas
- Link to people profiles

### Step 5: Update Knowledge & People

Based on check-in responses:
- Create or update knowledge documents
- Create or update people profiles
- Create wikilinks between related items
- Update time_invested in knowledge docs
- Update collaboration_time in people profiles

### Step 6: Create Retroactive Daily Note

For each missing day, create `knowledgebase/-common/Daily/YYYY-MM-DD.md`:

```markdown
# Daily Check-In - [Date]

*Captured retroactively on [current date]*

## Work Completed
- [Work description] - [duration] ([work_type])
  - Knowledge: [[Topic 1]], [[Topic 2]]
  - People: [[Person 1]]
- [Work description] - [duration] ([work_type])

## Time Summary
- Total time: X hours Y minutes
- By work type:
  - Technical: X hours
  - Meeting: Y hours
- Distractions: X minutes ([types])

## Knowledge & People
- Knowledge worked on: [[Topic 1]], [[Topic 2]]
- People interactions: [[Person 1]], [[Person 2]]

## Notes
- [Any blockers, challenges, or insights captured]

## Estimation Notes
- Work that took longer than expected: [description]
- Work that went faster: [description]
```

### Step 7: Update Session Tracker

Update `.system/session_tracker.json`:
- Set `last_daily_closeout` to most recent processed date
- Set `last_updated` to current timestamp
- Update `current_work` if work is ongoing
- Set `session_active` appropriately

### Step 8: Provide Summary

Show user what was captured:
```
✓ Captured work for [date1], [date2], [date3]
✓ Created X time entries (total: Y hours Z minutes)
✓ Updated knowledge: [[Topic 1]], [[Topic 2]]
✓ Updated people: [[Person 1]], [[Person 2]]
✓ Created daily notes for missing days
✓ Session tracker updated

All caught up! Ready to start today's work.
```

## Example Check-In Conversation

```
Agent: "I see it's been 3 days since we last talked. Let me catch up on what you did.

Did you work on Thursday, Dec 5?"

User: "Yes"

Agent: "What work did you do on Thursday?"

User: "Worked on API design, had a meeting with John about database architecture"

Agent: "How long did the API design work take?"

User: "About 2 hours"

Agent: "What type of work was that?"

User: "Technical"

Agent: "Any knowledge areas involved? I'm thinking [[API Design Patterns]]?"

User: "Yes, and also [[REST Architecture]]"

Agent: "Got it. Now the meeting with John - how long was that?"

User: "1 hour"

Agent: "I'll mark that as a meeting. Was it about [[Database Architecture]]?"

User: "Yes, and [[Data Migration]]"

Agent: "Any distractions or interruptions on Thursday?"

User: "Yeah, got pulled into an unplanned call, about 30 minutes"

Agent: "What did you learn or create on Thursday?"

User: "Learned about John's approach to schema versioning, should capture that"

Agent: "I'll create a note in [[Database Architecture]] about schema versioning and link it to [[John Smith]].

Anything blocking you or noteworthy from Thursday?"

User: "Need to follow up with John on the migration timeline"

Agent: "Noted. Let me create the time entries and update your knowledge base...

✓ Created 2 time entries for Thursday (3 hours total)
✓ Updated [[API Design Patterns]], [[REST Architecture]], [[Database Architecture]]
✓ Updated [[John Smith]]'s profile
✓ Created daily note for 2025-12-05

Now, did you work on Friday, Dec 6?"

[Continue for each missing day...]
```

## Integration with Startup Workflow

**Morning startup sequence:**
1. Get current date and time
2. Check session tracker for last interaction
3. Calculate time gap
4. If gap > 4 hours OR missing closeouts:
   - Run daily check-in workflow
   - Process all missing days
   - Update session tracker
5. Then proceed with normal startup

## Best Practices

**For the Agent:**
- Ask ONE question at a time
- Be patient - user is recalling past work
- Suggest knowledge areas and people based on descriptions
- Batch similar questions (all duration questions together)
- Provide clear summary of what was captured
- Don't make user repeat information

**For the User:**
- Be honest about time estimates (even rough)
- Mention people involved (helps build network)
- Note what you learned (builds knowledge)
- Capture distractions (improves patterns)
- It's okay to say "I don't remember" - estimate best you can

## Handling Edge Cases

**User doesn't remember details:**
- Accept rough estimates
- Focus on major work items
- Skip minor details
- Mark as "estimated" in notes

**Multiple days to catch up:**
- Process one day at a time
- Keep questions focused
- Provide progress updates ("2 of 3 days done")
- Allow breaks if needed

**User worked but didn't track anything:**
- That's okay! This is why check-in exists
- Capture what they remember
- Better to have rough data than no data
- Use for pattern analysis, not precise tracking

**Ongoing work across days:**
- Create separate time entries per day
- Link them with notes
- Track total time across entries
- Note in daily notes that work continued

## Tool Usage

**During check-in, use:**
- `start_work` and `end_work` to create retroactive time entries
- `create_knowledge` or `update_knowledge` for new learnings
- `create_person` or `update_person` for people mentions
- `link_person_to_knowledge` for connections
- `record_distraction` for interruptions captured

**After check-in, use:**
- `get_time_history` to verify entries created
- `get_session_status` to confirm tracker updated

## Success Criteria

Check-in is complete when:
- All missing days have been processed
- Time entries created for all work
- Knowledge and people updated
- Daily notes created for missing days
- Session tracker updated with current date
- User confirms summary is accurate

