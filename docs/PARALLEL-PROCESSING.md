# Parallel Processing Guide

## Overview

WorkOS now supports parallel processing using delegates to dramatically speed up operations. Instead of processing items sequentially, multiple AI delegates work simultaneously on independent tasks.

## Speed Improvements

- **Backlog Processing**: 10 items in ~30 seconds instead of 5 minutes
- **Task Analysis**: Multiple analyses in parallel instead of sequential
- **Daily Planning**: Get multiple perspectives simultaneously

## New MCP Tools

### 1. prepare_parallel_backlog_processing
Prepares backlog items for parallel delegate processing.

**Input:**
```json
{
  "include_existing_tasks": true
}
```

**Output:**
- List of backlog items
- Existing tasks for duplicate detection
- Delegate instructions
- Expected output format

### 2. prepare_parallel_task_analysis
Prepares task data for parallel analysis.

**Input:**
```json
{
  "analysis_types": ["priority", "category", "blockers", "goal_alignment", "time_estimates"]
}
```

**Output:**
- Task data grouped by analysis type
- Delegate configurations
- Context for each analysis

### 3. prepare_parallel_daily_planning
Prepares data for parallel daily planning.

**Input:**
```json
{
  "include_goals": true,
  "include_knowledge": false
}
```

**Output:**
- Time context (day, hour, etc.)
- Delegate configurations for different planning perspectives
- Goals and knowledge context

### 4. aggregate_parallel_results
Combines results from parallel delegates and takes actions.

**Input:**
```json
{
  "operation_type": "backlog_processing",
  "delegate_results": [...],
  "auto_create_tasks": false
}
```

**Output:**
- Aggregated summary
- Actions taken (if auto_create enabled)
- Recommendations

## Usage Examples

### Example 1: Fast Backlog Processing

```
User: "Clear my backlog"

AI:
1. prepare_parallel_backlog_processing()
2. Delegate tool with 10 parallel prompts (one per item)
3. aggregate_parallel_results(operation_type="backlog_processing", auto_create_tasks=true)
4. clear_backlog()

Result: 10 items processed in parallel, tasks created, backlog cleared
```

### Example 2: Comprehensive Task Analysis

```
User: "Give me a full analysis of my tasks"

AI:
1. prepare_parallel_task_analysis(analysis_types=["priority", "category", "blockers", "goal_alignment", "time_estimates"])
2. Delegate tool with 5 parallel analysis delegates
3. aggregate_parallel_results(operation_type="task_analysis")

Result: 5 different analyses completed simultaneously
```

### Example 3: Smart Daily Planning

```
User: "What should I work on today?"

AI:
1. prepare_parallel_daily_planning(include_goals=true)
2. Delegate tool with 3 parallel planning delegates:
   - Priority focus
   - Momentum tasks
   - Goal alignment
3. aggregate_parallel_results(operation_type="daily_planning")

Result: Recommendations from multiple perspectives, synthesized into actionable plan
```

## Delegate Configuration

Each delegate gets:
- **Full tool access**: Can call any MCP tool
- **Conversation context**: Sees the full conversation
- **Independent execution**: Runs in parallel with others
- **Structured output**: Returns JSON for easy aggregation

## Best Practices

1. **Use for 5+ items**: Overhead not worth it for fewer items
2. **Batch size**: Delegates run in batches of 10
3. **Clear instructions**: Each delegate needs specific task and output format
4. **Aggregate carefully**: Combine results intelligently, don't just concatenate

## Performance Notes

- **Sequential**: 10 backlog items = ~5 minutes (30s each)
- **Parallel**: 10 backlog items = ~30 seconds (all at once)
- **Batching**: 20 items = 2 batches of 10 = ~60 seconds

## Architecture

```
User Request
    ↓
prepare_parallel_* tool
    ↓
Delegate tool (parallel execution)
    ↓
aggregate_parallel_results
    ↓
Final actions & response
```

## Future Enhancements

Potential additions:
- Parallel knowledge base enrichment
- Parallel task dependency analysis
- Parallel time estimate refinement
- Parallel goal alignment scoring

## Troubleshooting

**Issue**: Delegates returning inconsistent formats
**Solution**: Ensure delegate instructions specify exact JSON structure

**Issue**: Aggregation missing data
**Solution**: Check delegate_results array structure matches expected format

**Issue**: Slower than expected
**Solution**: Verify batch size and number of items (overhead for <5 items)
