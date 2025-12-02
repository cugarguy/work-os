# Parallel Processing Quick Reference

## 🚀 Quick Commands

### Fast Backlog Processing
```
"Clear my backlog using parallel processing"
"Process my backlog items in parallel"
```

### Comprehensive Analysis
```
"Give me a full parallel analysis of my tasks"
"Analyze my tasks from all angles"
```

### Smart Daily Planning
```
"What should I work on today? Use parallel planning"
"Give me task recommendations from multiple perspectives"
```

## 📊 The 3 Workflows

### 1️⃣ Parallel Backlog Processing
```
prepare_parallel_backlog_processing()
    ↓
Delegate (N parallel item analyses)
    ↓
aggregate_parallel_results(operation_type="backlog_processing")
    ↓
clear_backlog()
```

**Speed**: 10 items in ~30 seconds (was 5 minutes)

### 2️⃣ Parallel Task Analysis
```
prepare_parallel_task_analysis(analysis_types=[...])
    ↓
Delegate (5 parallel analyses)
    ↓
aggregate_parallel_results(operation_type="task_analysis")
```

**Speed**: 5 analyses in ~30 seconds (was 5.5 minutes)

### 3️⃣ Parallel Daily Planning
```
prepare_parallel_daily_planning()
    ↓
Delegate (3 parallel planning perspectives)
    ↓
aggregate_parallel_results(operation_type="daily_planning")
```

**Speed**: 3 perspectives in ~20 seconds (was 3 minutes)

## 🛠️ The 4 New Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `prepare_parallel_backlog_processing` | Prep backlog for parallel processing | 5+ backlog items |
| `prepare_parallel_task_analysis` | Prep tasks for parallel analysis | Want comprehensive view |
| `prepare_parallel_daily_planning` | Prep for parallel planning | Daily/weekly planning |
| `aggregate_parallel_results` | Combine delegate results | After parallel delegates run |

## ⚡ Performance Cheat Sheet

| Items | Sequential | Parallel | Speedup |
|-------|-----------|----------|---------|
| 5 items | 2.5 min | 25 sec | 6x |
| 10 items | 5 min | 30 sec | 10x |
| 20 items | 10 min | 60 sec | 10x |
| 50 items | 25 min | 2.5 min | 10x |

## 🎯 Analysis Types

For `prepare_parallel_task_analysis`:

- **priority** - Priority distribution and balance
- **category** - Work distribution by category
- **blockers** - Identify blockers and unblocking actions
- **goal_alignment** - How tasks align with goals
- **time_estimates** - Workload and timeline analysis

Use all 5 for comprehensive analysis!

## ✅ When to Use Parallel

### Use Parallel When:
- ✅ 5+ backlog items
- ✅ Multiple analyses needed
- ✅ Daily/weekly planning
- ✅ Comprehensive reviews
- ✅ Independent subtasks

### Use Sequential When:
- ❌ 1-2 items
- ❌ Sequential dependencies
- ❌ Simple queries
- ❌ Single perspective needed

## 🔧 Troubleshooting

**Not seeing new tools?**
→ Restart MCP server in Kiro

**Slower than expected?**
→ Need 5+ items for speedup

**Inconsistent results?**
→ Check delegate instructions

**Missing data?**
→ Verify delegate_results format

## 📚 Documentation

- `PARALLEL-UPGRADE.md` - What changed
- `docs/PARALLEL-PROCESSING.md` - Complete guide
- `examples/parallel-backlog-example.md` - Backlog example
- `examples/parallel-analysis-example.md` - Analysis example

## 💡 Pro Tips

1. **Batch operations**: Process backlog weekly, not daily
2. **Use all analyses**: Get comprehensive view with all 5 analysis types
3. **Auto-create**: Use `auto_create_tasks=true` for trusted backlog items
4. **Review duplicates**: Always check flagged duplicates before merging
5. **Time context**: Run daily planning in morning for best recommendations

## 🎬 Example Session

```
User: "I have 15 items in my backlog"

AI: "I'll process those in parallel for speed!"
    1. prepare_parallel_backlog_processing()
    2. Delegate(15 parallel analyses)
    3. aggregate_parallel_results(auto_create_tasks=true)
    4. clear_backlog()

Result: "✅ Created 12 tasks, found 2 duplicates, 1 needs clarification
         Total time: ~40 seconds"
```

## 🚦 Status Indicators

When AI uses parallel processing, you'll see:
- 🔄 "Processing in parallel..."
- ⚡ "Using N delegates..."
- ✅ "Parallel processing complete!"
- 📊 "Aggregating results..."

## 🎯 Remember

**The Rule of 5**: If you have 5+ items, use parallel processing!

**Speed Formula**: 
- Sequential: N items × 30 seconds = N/2 minutes
- Parallel: ~30 seconds regardless of N (up to 10)
- Batching: 10+ items = ceil(N/10) × 30 seconds

**Best Use Cases**:
1. Weekly backlog clearing (10-20 items)
2. Monthly task reviews (comprehensive analysis)
3. Daily planning (multiple perspectives)
4. Quarterly goal alignment checks
