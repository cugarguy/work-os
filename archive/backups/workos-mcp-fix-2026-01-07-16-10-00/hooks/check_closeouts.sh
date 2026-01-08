#!/bin/bash

TODAY=$(date +"%Y-%m-%d")
DAY_OF_WEEK=$(date +"%A")
YESTERDAY=$(date -v-1d +"%Y-%m-%d")

TRACKER=".system/session_tracker.json"

if [ ! -f "$TRACKER" ]; then
    echo "SESSION_START: Today is $DAY_OF_WEEK, $TODAY"
    exit 0
fi

LAST_DAILY=$(jq -r '.last_daily_closeout // "null"' "$TRACKER")
LAST_WEEKLY=$(jq -r '.last_weekly_closeout // "null"' "$TRACKER")

MISSING=""

# Check yesterday's closeout
if [ "$LAST_DAILY" != "$YESTERDAY" ] && [ "$LAST_DAILY" != "$TODAY" ]; then
    MISSING="MISSING_DAILY_CLOSEOUT: $YESTERDAY"
fi

# Check weekly closeout on Monday
if [ "$DAY_OF_WEEK" = "Monday" ]; then
    LAST_FRIDAY=$(date -v-Fri -v-7d +"%Y-%m-%d")
    if [ "$LAST_WEEKLY" != "$LAST_FRIDAY" ] && [ "$LAST_WEEKLY" \< "$LAST_FRIDAY" ]; then
        if [ -n "$MISSING" ]; then
            MISSING="$MISSING AND MISSING_WEEKLY_CLOSEOUT: week ending $LAST_FRIDAY"
        else
            MISSING="MISSING_WEEKLY_CLOSEOUT: week ending $LAST_FRIDAY"
        fi
    fi
fi

if [ -n "$MISSING" ]; then
    echo "SESSION_START: Today is $DAY_OF_WEEK, $TODAY. $MISSING - Run closeout workflow first."
else
    echo "SESSION_START: Today is $DAY_OF_WEEK, $TODAY. All closeouts current."
fi
