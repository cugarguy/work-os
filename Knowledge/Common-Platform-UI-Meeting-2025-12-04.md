# Common Platform UI Meeting - 2025-12-04

## Meeting Info
- **Date:** 2025-12-04
- **Topic:** Local Console UI Review - Phoenix/Tenon Pivot
- **Context:** Phoenix project/team has pivoted to Common Platform effort

## Overview
Engineering team conducted comprehensive review of local console UI mockups, focusing on troubleshooting utilities, network settings, and file system management capabilities. Session covered three main areas: network troubleshooting tools, AWS connectivity testing, and file system operations.

## Key Design Decisions

### Venn Diagram Approach
- Local console functionality should be a subset of regional console capabilities
- Exceptions require specific justification
- Ensures customers can perform most operations through either interface while maintaining consistency

### Architecture
- Services can select which features they want
- Widgets and micro consoles approach
- Two separate consoles: Phoenix console vs Common Platform console
- Left navigation will guide service teams in building and using common platform

## Troubleshooting and Connectivity Tools

### Categories of Diagnostic Tools
- Network connectivity tests: DNS, firewall, MTU
- AWS service connectivity tests: S3, IAM, Phoenix endpoints
- Downloadable diagnostic reports

### Design Principles
- Focus on common issues identified through existing support channels
- Don't attempt to create comprehensive network diagnostic applications
- Provide clear English explanations of test results
- Maintain access to raw technical output for advanced users
- Organize tests by service rather than technical implementation
- Provide actionable guidance for common failures
- Ensure tools work effectively in disconnected scenarios

### Error Messaging Approach
- Good English error messaging is the starting point
- Run multi-step tests
- Allow customers to use other settings
- Design tests to help customers without dumbing it down
- Tell them what we did and what results we got
- [These standards are actually applicable to the full system, not just the local console]

### Support Tools
- Build other "support tools" that customers can download and use
- Need designs for logs and other test output information

### AWS Connectivity Tests
- Network works but things aren't working with AWS elements
- Question: If there are issues, should we send them to the main console?
- Separation: All endpoints are not available vs just one endpoint
- Endpoints and labels that mean something to customers - transparent without getting into unnecessary weeds

### Documentation
- Ideally: Documentation accompanies local console, use as fallback

## Network Configuration and Safety

### Auto-Rollback Functionality
- Network settings management is critical but complex
- Auto-rollback to prevent configuration changes from locking out administrators
- Similar to enterprise router patterns
- Questions about which network settings belong in local vs regional consoles
- Traffic shaping and advanced configurations potentially remain in regional interfaces

## Reboot/Restart Options
- Restarting the VM vs restarting the container or the service
- Run a set of tests for various areas and decide what to do with results
- Question: How much is for us vs for the customer?

## Authentication and Disconnected State

### Local Authentication
- Do we need readonly access?
- Do we need half admin vs full admin?
- May need a full meeting on its own
- Do we need to access the serial console? (Would need same password and access)
- **Tenon will own this conversation**
- PMs need to say what customers want and what AppSec will allow
- **Tenon will own the serial console**
- **Tenon owns setting up the meeting**

### Disconnected State
- Many distinctions in disconnected state
- Platform can survive for 12 months when certificate expires
- **Bob (me) will own the disconnected state conversation/doc**
- Cordell suggested a list of disconnected tenets - what is disconnected mode

## File System Management

### Snapshots
- Discussion: Whether and how snapshots would work on local console
- **Decision: Allow customers to take snapshots, but not restore the full filesystem**
- Manual snapshot creation and basic management capabilities needed during disconnected scenarios
- Self-service restore capabilities supported
- Full file system restores remain restricted due to destructive nature and complexity in disconnected environments

## Decisions

1. Local console will follow a Venn diagram approach where all local console functionality is also available in the regional console, with exceptions to be debated case-by-case
2. Troubleshooting tools will focus on common issues based on existing support experience rather than trying to solve all possible network problems
3. Network configuration changes will include auto-rollback functionality with override options to prevent accidental lockouts
4. File system snapshots and basic management will be available locally for disconnected scenarios
5. Authentication and disconnected state requirements need dedicated meetings to resolve before UI implementation

## Action Items

- [ ] Console team: Create list of local console features that cannot be done in regional console
- [ ] Bob (me): Define disconnected state tenets
- [ ] Common platform team: Provide list of out-of-box console components for Phoenix and other services
- [ ] Tenon team: Schedule and own authentication (auth) requirements meeting
- [ ] Tenon team: Resolve network configuration rollback implementation approach

## Related
- [[Phoenix UX]]
- [[Common Platform]]
- [[Tenon]]
