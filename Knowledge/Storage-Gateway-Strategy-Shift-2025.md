---
title: "Storage Gateway Strategic Shift - 2025"
created_date: 2025-12-12
updated_date: 2025-12-12
tags:
  - storage-gateway
  - strategy
  - ktlo
  - phoenix
  - resource-allocation
related_people: []
time_invested: 0
---

# Storage Gateway Strategic Shift - 2025

## Major Strategic Change

**Decision:** Storage Gateway moving to KTLO (Keep The Lights On) mode effective 2025

## Phoenix Project Status

**Project:** Single site NAS replacement offering leveraging FSx for OpenZFS's S3 Block driver
**Status:** **PAUSED/CANCELLED**
**Rationale:** 
- Demand signals for hybrid storage offering not as strong as expected
- MFT market showing stronger demand signals
- Resource reallocation needed for higher-impact initiatives

## Current SGW Performance

### Financial Performance
- **YTD Revenue:** $24.1M (-8.3% YoY, -3.8% vs. OP2)
- **4-week ARR:** $25.8M (-3% vs. OP2)
- **Customer Count:** Declining -14% YoY

### Revenue Breakdown
- **Data Storage:** $21.3M (434PB, -0.5% YoY)
  - Volume storage declining -8.4% YoY
  - Tape storage growing modestly +1.2% YoY but revenue down -3.9% YoY
- **Data Ingest:** $1.74M (902PB, +6.1% YoY)

## KTLO Mode Operations

### Investment Limitations
- **Allowed:** Durability improvements, campaigns, patching, region launches
- **Minimal HC:** Maintain AWS operational bar with minimal headcount
- **No New Features:** No new feature launches planned

### Resource Reallocation
**From:** Storage Gateway feature development
**To:** 
- MFT (Managed File Transfer) capabilities
- Tenon platform development
- Transfer Family and DataSync enhancements

## Impact on Team and Resources

### Engineering Resources
- SGW engineering resources shifting to:
  - Transfer Family MFT features
  - DataSync Enhanced mode
  - Tenon platform development

### Product Management
- Continued support for existing customers
- Focus on operational excellence
- Migration path planning for customers

## WBR Presentation Insights - December 16, 2025

### Leadership Feedback Analysis
- **John's Focus:** Immediately went to churn analysis - expected given KTLO status
- **Jody's Priority:** "Putting VGW to bed" - strong signal for sunset consideration
- **Strategic Reality:** Limited content to review due to KTLO mode

### Gateway Sunset/Maintenance Analysis

#### Volume Gateway (VGW)
- **Leadership Signal:** Jody wants VGW "put to bed"
- **Assessment:** Wouldn't take much analysis to consider for sunset
- **Next Steps:** Sunset analysis and documentation

#### Tape Gateway (TGW)  
- **Alternative Path:** Could transition to maintenance mode
- **Assessment:** Analysis wouldn't be difficult
- **Positioning:** Less aggressive than sunset, maintenance-focused

### Strategic Opportunity with Smitha
- **Opportunity:** Lead documentation and analysis for VGW sunset and TGW maintenance
- **Benefit:** Could improve relationship by taking initiative on strategic docs
- **Approach:** Present comprehensive analysis and recommendations

## Customer Impact

### Existing Customers
- **Continued Support:** Full operational support maintained
- **No Disruption:** Existing deployments continue operating
- **Migration Options:** Guidance toward alternative solutions

### New Customers
- **Limited Onboarding:** Minimal new customer acquisition efforts
- **Alternative Solutions:** Directing to FSx, DataSync, or other AWS storage services

## Alternative Solutions for SGW Use Cases

### File Gateway Replacement
- **Amazon FSx:** For high-performance file systems
- **DataSync:** For data transfer and synchronization
- **S3 Direct:** For cloud-native applications

### Volume/Tape Gateway Replacement
- **AWS Backup:** For backup use cases
- **S3 Glacier:** For archival storage
- **DataSync:** For migration scenarios

## Timeline and Milestones

### 2025
- Phoenix project officially paused
- Resource reallocation begins
- KTLO mode implementation

### 2026
- Continued KTLO operations
- Tenon platform development (SGW integration planned for 2027)
- Customer migration guidance and support

## Strategic Rationale

### Market Analysis
- **MFT Market:** $3-4B market with 10% CAGR showing stronger demand
- **Hybrid Storage:** Demand signals weaker than anticipated
- **Customer Behavior:** Shift toward cloud-native solutions

### Resource Optimization
- **Higher ROI:** MFT investments showing better returns
- **Platform Efficiency:** Tenon will reduce operational burden long-term
- **Focus:** Concentrate on growth areas rather than declining segments

## Related Work
- [[EDS-MBR-December-2025]]
- [[Tenon Platform Initiative]]
- [[MFT Strategy]]
