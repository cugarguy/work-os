---
inclusion: always
---

# Daily & Weekly Closeout Workflows

## Morning Startup Check

Every morning when starting work:
1. Check if previous day was closed out
2. If not closed out → Run daily closeout for previous day FIRST
3. Then start current day

Every Monday morning:
1. Check if previous week was closed out
2. If not closed out → Run weekly closeout for previous week FIRST
3. Then start current week

## Daily Closeout Workflow

Trigger phrases: "close out today", "end of day", "daily closeout"

**Interaction Style:**
- Ask ONE question at a time
- Wait for response before asking next question
- Keep questions focused and specific
- Don't batch multiple questions together

**Steps:**
1. **Process notes inbox FIRST**: Check if NOTES_INBOX.md has items
   - If yes → Run notes processing workflow
   - Process items ONE AT A TIME
   - Clear inbox before continuing closeout

2. **Review today's time entries**: Use `get_time_history` with `days=1`
   - Show all work completed today
   - Calculate total time by work type
   - Identify any open/incomplete time entries

3. **Review knowledge and people updates**:
   - Ask: "What knowledge did you create or update today?"
   - Ask: "Who did you interact with or learn about today?"
   - Note any new wikilinks or connections made

4. **Gather reflections**:
   - What work took longer than expected? Why?
   - What work went faster than expected? Why?
   - Any distractions or interruptions? (use distraction data from time entries)
   - What did you learn today?
   - Any blockers or challenges?

5. **Create summary in `daily-notes/YYYY-MM-DD.md`**:
   ```markdown
   # Daily Closeout - [Date]
   
   ## Work Completed
   - [Work description] - [duration] ([work_type])
   - [Work description] - [duration] ([work_type])
   
   ## Time Summary
   - Total productive time: X hours Y minutes
   - By work type:
     - Technical: X hours
     - Writing: Y hours
     - Research: Z hours
   - Distractions: X minutes ([types])
   
   ## Knowledge & People
   - Knowledge created/updated: [[Topic 1]], [[Topic 2]]
   - People interactions: [[Person 1]], [[Person 2]]
   - New connections made: [[Topic]] ↔ [[Person]]
   
   ## Reflections
   - What went well:
   - What took longer than expected:
   - What I learned:
   - Blockers or challenges:
   
   ## Tomorrow's Focus
   - Continue work on: [description]
   - Explore: [knowledge area]
   - Connect with: [person]
   ```

6. **Update session tracker** with closeout completion date

7. **Suggest tomorrow's focus** based on:
   - Incomplete work from today
   - Knowledge areas needing attention
   - People to follow up with

## Weekly Closeout Workflow

Trigger phrases: "close out this week", "weekly closeout", "end of week"

**Steps:**
1. **Review week's time entries**: Use `get_time_history` with `days=7`
   - Show all work completed this week
   - Calculate total time by work type
   - Calculate total time by knowledge area
   - Calculate total time by people (collaboration)

2. **Analyze patterns**: Use analysis tools
   - `get_distraction_analysis` with `days=7` - distraction patterns
   - `get_expertise_analysis` - knowledge areas by time investment
   - `get_collaboration_analysis` with `days=7` - collaboration patterns
   - `get_time_trends` - time distribution trends

3. **Review knowledge growth**:
   - Ask: "What new knowledge did you create this week?"
   - Ask: "What existing knowledge did you significantly update?"
   - Count new wikilinks and connections made
   - Identify knowledge areas that need more attention

4. **Review people interactions**:
   - Ask: "Who did you collaborate with most this week?"
   - Ask: "Any new people you met or learned about?"
   - Review collaboration time vs solo work time
   - Note any relationship changes or new connections

5. **Gather reflections**:
   - Major accomplishments this week
   - Estimation accuracy (estimates vs actuals)
   - Distraction patterns observed
   - Knowledge areas that consumed most time
   - Collaboration effectiveness
   - What you learned about your work patterns

6. **Create summary in `daily-notes/weekly-closeout-YYYY-MM-DD.md`**:
   ```markdown
   # Weekly Closeout - Week of [Date]
   
   ## Work Summary
   - Total time: X hours Y minutes
   - By work type:
     - Technical: X hours (Y%)
     - Writing: X hours (Y%)
     - Research: X hours (Y%)
     - Meetings: X hours (Y%)
   - Average per day: X hours
   
   ## Knowledge Growth
   - New knowledge created: [[Topic 1]], [[Topic 2]]
   - Significant updates: [[Topic 3]], [[Topic 4]]
   - Total knowledge areas worked on: X
   - Most time invested: [[Topic]] (X hours)
   
   ## People & Collaboration
   - Collaborated with: [[Person 1]] (X hours), [[Person 2]] (Y hours)
   - New connections: [[Person 3]]
   - Solo work: X% | Collaborative work: Y%
   
   ## Time Intelligence
   - Estimation accuracy: [Good/Needs improvement]
   - Work that took longer: [description and why]
   - Work that went faster: [description and why]
   - Distraction patterns: [peak times, common types]
   
   ## Reflections
   - Major wins:
   - Challenges:
   - Patterns noticed:
   - What I learned about my work style:
   
   ## Next Week's Focus
   - Knowledge areas to explore: [[Topic]]
   - People to connect with: [[Person]]
   - Work patterns to improve: [description]
   - Time management adjustments: [description]
   ```

7. **Update session tracker** with weekly closeout completion date

8. **Suggest next week's focus** based on:
   - Knowledge areas needing attention
   - People to follow up with
   - Work patterns to improve
   - Time management insights

## Session Tracker Updates

The session tracker (`.system/session_tracker.json`) should track:
- `last_daily_closeout`: Date of last daily closeout (YYYY-MM-DD)
- `last_weekly_closeout`: Date of last weekly closeout (YYYY-MM-DD)
- `current_week_start`: Monday of current week (YYYY-MM-DD)

## Closeout Completion Criteria

**Daily closeout is complete when:**
- Summary created in daily-notes/
- All time entries reviewed
- Knowledge and people updates noted
- Reflections captured
- Tomorrow's focus identified
- Session tracker updated

**Weekly closeout is complete when:**
- Summary created in daily-notes/
- All week's time entries reviewed
- Patterns analyzed (distractions, expertise, collaboration)
- Knowledge growth assessed
- People interactions reviewed
- Next week's focus identified
- Session tracker updated

## Integration with Knowledge & Time System

- Daily closeout captures time data for analysis
- Weekly closeout provides pattern insights
- Closeout data improves time estimates
- Distraction tracking identifies productivity patterns
- Knowledge tracking shows learning and growth
- People tracking reveals collaboration patterns
- Reflections improve self-awareness and work habits
