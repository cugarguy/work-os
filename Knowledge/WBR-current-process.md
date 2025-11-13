# WBR Assistant - Requirements & Process Documentation

Documentation for building WBR assistant in Kiro.

## What the Assistant Needs

1. WBR formatting guidelines - The official standards for how WBRs should be structured and written
2. Gold standard examples - Sample WBRs that represent the quality and style you're aiming for
3. Any specific rules - Writing conventions, metrics presentation standards, narrative guidelines, etc.

## Current WBR Process Steps

1. Calculate ARR (The average of the last 4 weeks of revenue * 52 weeks)
2. Adjust weekly spreadsheet to remove attributed revenue (Volume gateway Snapshots) - Volume is on ingest and storage)
3. Create YTD YoY metrics - act rev, plan rev, diff, diff %
   - Apply to all services
   - Apply to usage too 
4. Calculate YTD YoY and YTD growth for accounts and gateways
5. [INCOMPLETE - need to document this step]

## Notes

- Volume gateway: only count ingest and storage, not snapshots
- YTD YoY metrics need to be applied consistently across services and usage data
