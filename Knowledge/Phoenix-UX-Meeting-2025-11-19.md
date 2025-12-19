# Phoenix UX Meeting - November 19, 2025

**Related:** [[Common-Platform-UI-Meeting-2025-12-04]] - Follow-up meeting on local console design

## Meeting Info
- **Date:** 2025-11-19
- **Topic:** Phoenix UX
- **Attendees:** 
  - Mike (front end engineer)
  - Jeremy (front end engineer)
  - Rowan (engineer)
  - Alex (engineer)

## Notes

- Mike and Jeremy are in THS region build hell - context switching to this meeting
- Rowan joined and made a joke
- Alex joined
- Football talk: Drake Maye, NE Patriots (with Mike)

### Local Console Experience & Activation
- Discussing how customers activate an appliance
- Customer gets an activation key and enters it
- Question: How much info does the activation key contain?
- Alex is pushing for more information in the activation key

### Networking & Console Management
- Cross talk about how much networking gets handled in the local console
- Overlap with Unified Platform (underlying part of the stack)
- Bassem wants to limit networking capabilities to only things that won't break the connection
- Discussion about what is in region vs on local console
- Linking the gateway to AWS console and vice versa
- **Core question:** Where do we provide the customer the access and tools they need to manage this appliance in their environment?

### Authentication & Security
- 2-factor auth provided by Tenon (Tenon = Unified Platform)
- How to authenticate locally for admin (may not be in this part of UX flow)
- Alex suggests AppSec involvement - how to recover passwords
- Should tie into customer auth (Active Directory)
- Still need solution for customers who don't have AD
- Lots of questions around password management

### Disk Selection
- Current approach is more complicated, need to rethink
- Disks are not "selected" - customer gives permission to use the disks
- Process flow: Activation first (ensures connection between local and region), then all other steps take place
- No need to have an Accept License screen

### Review Cadence
- Conversation about how to get through reviews quicker
- An hour a week is not enough to meet the deadline
- Mike will look to book more time in the coming weeks

## Action Items
- [ ] Review Phoenix UX mocks and provide feedback/input
- [ ] Mike to book more review time in coming weeks

## Follow-up
- 

## Related
- [[2-knowledgebase/Phoenix/Project-Management/Project: Phoenix]]
