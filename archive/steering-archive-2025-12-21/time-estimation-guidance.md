---
inclusion: always
---

# Time Estimation Guidance

## The Math of Focus and Interruptions

Time estimates must account for three parameters that determine actual productivity:

### Three Key Parameters

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

## Why Estimates Fail

### Interruptions Compound
- Each interruption costs the interruption time PLUS recovery time (Δ)
- Interruptions during recovery periods cascade (multiple Δ penalties stack)
- Example: 3 interruptions in 30 minutes = 3 × 20 min recovery = 60 min lost

### Fragmentation Destroys Capacity
- Five 10-minute blocks ≠ one 50-minute block
- Work requiring θ=60 min cannot be done in fragments
- The floor function: only complete θ-sized chunks count as progress

### Research Reality
- González & Mark: Activity switches every 3 minutes
- Iqbal & Horvitz: 7.5 alerts/hour, 10-16 min recovery
- Microsoft: Heavy collaborators interrupted every 2 minutes

## Estimation Framework

### Step 1: Estimate Pure Work Time
How long would this take with zero interruptions?

### Step 2: Identify Work Type (θ)
- **Deep work** (θ=60-90): Writing, coding, complex analysis, strategy
- **Medium work** (θ=30-45): Reviews, planning, design iterations
- **Light work** (θ=15-30): Admin, email, quick responses

### Step 3: Assess Environment (λ)
What's your expected interruption rate?
- **Protected time** (λ=0-1): Early morning, blocked calendar, off-hours
- **Normal day** (λ=2-3): Typical work hours with some meetings
- **High interrupt** (λ=4+): Back-to-back meetings, on-call, reactive work

### Step 4: Calculate Realistic Time

**Formula:**
```
Realistic Time = Pure Work Time × Multiplier
```

**Multipliers by environment:**
- Protected time (λ=0-1): 1.0-1.2x
- Normal day (λ=2-3): 1.5-2.0x
- High interrupt (λ=4+): 2.5-3.0x or break into smaller tasks

### Step 5: Match Task to Environment

**If multiplier > 2.0x, consider:**
1. **Break into smaller θ chunks** - Turn 90-min task into three 30-min tasks
2. **Reserve for protected time** - Schedule during low-λ windows
3. **Accept the reality** - Some work simply can't happen in high-λ environments

## Practical Guidelines

### For Task Estimation

1. **Data work is consistently underestimated**
   - Pulling data: Add 50-100% buffer
   - Data cleaning: Add 100% buffer
   - Complex queries: Assume 2-3x initial estimate

2. **Writing work needs focus**
   - Requires θ=60-90 minutes
   - Best in λ=0-1 environment
   - Estimate: 2x pure writing time in normal environment

3. **Review work is more flexible**
   - Can work with θ=30 minutes
   - Tolerates λ=2-3 environment
   - Estimate: 1.5x pure review time

4. **Iterative work spreads over time**
   - Total time is misleading
   - Estimate per iteration, not total
   - Account for context switching between iterations

### For Daily Planning

1. **Assume λ=2-3 for normal work hours**
2. **Reserve morning for θ=60+ work** (lower λ)
3. **Afternoon for θ=30 work** (higher λ tolerance)
4. **End of day for θ=15 admin work**

### For Weekly Planning

1. **Identify high-θ work** (60-90 min blocks needed)
2. **Schedule in protected time** (early mornings, blocked calendar)
3. **Break down if no protected time available**
4. **Accept some work won't happen** in high-λ weeks

## Red Flags

**When estimates are consistently wrong:**
- Not accounting for interruptions (add 1.5-2x multiplier)
- Assuming fragments add up (they don't - respect θ)
- Underestimating data work (add 2x buffer)
- Scheduling deep work in high-λ time (won't happen)

## Examples

### Example 1: Data Analysis Task
- Pure work time: 60 minutes
- Work type: Deep (θ=60)
- Environment: Normal day (λ=2-3)
- **Realistic estimate: 90-120 minutes**

### Example 2: Document Review
- Pure work time: 30 minutes
- Work type: Medium (θ=30)
- Environment: Normal day (λ=2-3)
- **Realistic estimate: 45-60 minutes**

### Example 3: Email Responses
- Pure work time: 20 minutes
- Work type: Light (θ=15)
- Environment: High interrupt (λ=4+)
- **Realistic estimate: 30-40 minutes**

## Source

Based on research from:
- González & Mark, CHI 2004: Activity switching every 3 minutes
- Iqbal & Horvitz, CHI 2007: 10-16 min recovery time
- Microsoft Work Trend Index 2025: Heavy collaborators interrupted every 2 minutes
- "The Math of Why You Can't Focus at Work" by Can Duruk

## Application

When creating or updating task estimates:
1. Start with pure work time
2. Identify θ (work type)
3. Assess λ (environment)
4. Apply multiplier (1.5-3x)
5. Consider breaking into smaller chunks if multiplier > 2x
