---
title: "Tenon Platform Initiative"
created_date: 2025-12-12
updated_date: 2025-12-12
tags:
  - tenon
  - platform
  - edge-deployments
  - operational-efficiency
  - datasync
  - storage-gateway
related_people: []
time_invested: 0
---

# Tenon Platform Initiative

## Overview

**Tenon** is a new internal service designed to eliminate redundant work across AWS service teams that offer edge products, providing a common platform for building, deploying, and maintaining software instances distributed by AWS and deployed in customer environments.

## Problem Statement

### Current Challenges
- **Redundant Work:** Multiple teams (DataSync, Storage Gateway, AWS Backup, DRS) building similar edge deployment capabilities
- **Operational Burden:** Each service maintains separate infrastructure for customer environment deployments
- **Inefficiency:** Duplicated effort across teams for common edge deployment patterns

## Solution: Unified Edge Platform

### Core Capabilities
- **Software Image Generation:** Standardized process for creating deployable images
- **Activation and Authentication:** Common authentication and activation mechanisms
- **Container Orchestration:** Unified container management for edge deployments
- **Disk Management:** Standardized storage management across services
- **Basic Monitoring:** Common monitoring and observability framework

## Target Services

### Initial Scope
1. **AWS Backup** (RipTide launch - MVP target)
2. **Storage Gateway** (2027 integration)
3. **DataSync** (2027 integration)

### Future Expansion
- **AWS DRS** (Disaster Recovery Service)
- Other AWS services with on-premises deployment needs

## Timeline and Milestones

### 2026 Goals
- **MVP Delivery:** Support AWS Backup RipTide launch
- **Functional POC:** Early Q1'26 demonstration of core service components
- **PRFAQ Development:** Q1'26 architecture finalization

### 2027 Goals
- **SGW Integration:** Migrate Storage Gateway to Tenon platform
- **DataSync Integration:** Migrate DataSync edge components to Tenon

## Expected Benefits

### Operational Efficiency
- **Reduced Development Time:** Common platform eliminates duplicate development
- **Lower Maintenance Overhead:** Centralized platform maintenance
- **Standardized Operations:** Consistent operational procedures across services

### Service Teams Impact
- **DataSync Team:** Reduced operational burden for agent management
- **Storage Gateway Team:** Simplified edge deployment and maintenance
- **AWS Backup Team:** Faster time-to-market for RipTide

### Customer Benefits
- **Consistent Experience:** Unified deployment and management experience
- **Improved Reliability:** Battle-tested platform components
- **Enhanced Security:** Centralized security model and updates

## Technical Architecture

### Core Components (POC Scope)
1. **Image Builder:** Automated software image generation pipeline
2. **Activation Service:** Customer environment activation and registration
3. **Auth Framework:** Secure authentication between edge and AWS
4. **Container Runtime:** Orchestration layer for edge workloads
5. **Storage Manager:** Disk and storage resource management
6. **Monitoring Agent:** Basic telemetry and health monitoring

## Development Approach

### Phase 1: MVP (2026)
- **Focus:** AWS Backup RipTide support
- **Scope:** Core platform components
- **Goal:** Prove platform viability

### Phase 2: Migration (2027)
- **Focus:** SGW and DataSync integration
- **Scope:** Service-specific adaptations
- **Goal:** Operational efficiency gains

## Success Metrics

### Operational Metrics
- **Development Velocity:** Faster feature delivery for edge services
- **Operational Overhead:** 25-50% reduction in maintenance effort
- **Time to Market:** Reduced launch time for new edge services

### Platform Adoption
- **Service Integration:** Number of services successfully migrated
- **Customer Satisfaction:** Edge deployment experience improvements
- **Reliability:** Platform uptime and stability metrics

## Strategic Alignment

### EDS Strategy
- **Resource Optimization:** Aligns with shift from SGW feature development
- **Operational Excellence:** Supports 2026 operational efficiency goals
- **Platform Thinking:** Enables future edge service innovations

### AWS-Wide Benefits
- **Reusability:** Platform available for other AWS teams
- **Standards:** Establishes best practices for edge deployments
- **Innovation:** Enables new edge service possibilities

## Related Work
- [[Storage-Gateway-Strategy-Shift-2025]]
- [[EDS-MBR-December-2025]]
- [[AWS Backup RipTide]]
