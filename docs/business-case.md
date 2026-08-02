# FlowLens Business Case

## Document Purpose

This document defines the fictional organization, business problem, transformation opportunity, project boundaries, and intended outcomes for FlowLens.

FlowLens will demonstrate how a systems analyst can evaluate a fragmented operating environment, preserve the parts that work, redesign the parts that do not, and implement a measurable future state.

## Organization Profile

### Company

Northstar Business Services

### Industry

Business services and implementation consulting

### Company Size

Approximately 450 employees across Sales, Legal, Finance, Implementation, Operations, and Executive Leadership.

### Business Model

Northstar sells implementation and managed-service engagements to mid-sized organizations.

After a contract is signed, every customer must move through a cross-functional contract-to-launch process before service delivery can begin.

## Current Business Process

The contract-to-launch process begins when Sales marks an opportunity as closed-won.

The customer must then move through:

1. Contract verification
2. Legal approval
3. Billing setup
4. Implementation planning
5. Resource assignment
6. Technical readiness review
7. Customer launch
8. Operational handoff

Multiple departments participate, but no single system manages the complete process.

## Current System Landscape

| System | Primary Purpose | What Currently Works |
|---|---|---|
| Salesforce | Customer and opportunity records | Sales data is structured and broadly trusted |
| DocuSign | Contract signatures and executed agreements | Signed documents are reliable and accessible |
| Google Sheets | Master launch tracker | Flexible and familiar to operational teams |
| Gmail | Legal and finance approvals | Supports detailed conversations and attachments |
| Slack | Internal notifications and urgent coordination | Fast communication and high adoption |
| Jira | Implementation tasks and technical work | Effective for structured execution after tasks are created |
| NetSuite | Billing accounts and financial records | Trusted source for billing status |

## Current-State Workflow

When an opportunity closes:

1. A Sales representative updates Salesforce.
2. The representative manually enters the customer into a shared Google Sheet.
3. The contract is located in DocuSign and linked in the spreadsheet.
4. Sales emails Legal and Finance for review.
5. Approval responses remain inside separate email threads.
6. An Operations coordinator monitors the spreadsheet for updates.
7. The coordinator creates a Jira implementation project.
8. Customer information is manually copied into Jira.
9. Finance creates the billing account in NetSuite.
10. Implementation assigns resources and begins readiness work.
11. Status updates are posted in Slack and manually copied back into the spreadsheet.
12. Operations decides when the customer is ready to launch.
13. The completed launch is handed to the service-delivery team.

## What Is Working

FlowLens will not assume that every existing system must be replaced.

The following capabilities should be preserved:

- Salesforce remains the source of truth for opportunity and customer data.
- DocuSign remains the source of truth for executed agreements.
- NetSuite remains the source of truth for billing readiness.
- Jira remains the primary execution system for implementation work.
- Slack remains the preferred notification channel.
- Department specialists retain authority over legal, financial, and readiness decisions.
- The current process contains necessary control points that should not be removed merely for speed.

## Current Problems

### Fragmented Process Ownership

No person or system has a complete, reliable view of the contract-to-launch lifecycle.

### Duplicate Data Entry

Customer and contract information is manually copied between Salesforce, Google Sheets, Jira, email, and NetSuite.

### Inconsistent Status Definitions

Each department uses different language to describe progress. A customer may appear ready in one system and blocked in another.

### Invisible Approvals

Legal and financial decisions remain inside email threads and cannot be reliably included in operational reporting.

### Weak Handoffs

Work frequently stalls between departments because ownership and next actions are unclear.

### Delayed Exception Detection

Teams often discover missing contracts, billing issues, or incomplete technical requirements only after a target date is at risk.

### Manual Reporting

Leadership reporting depends on spreadsheet maintenance and individual status updates.

### Limited Auditability

The company cannot easily reconstruct who approved a launch, when requirements were completed, or why a decision changed.

## Business Impact

The fragmented workflow creates:

- Longer customer-launch cycle times
- Repeated administrative work
- Missed or delayed approvals
- Inconsistent customer experiences
- Unclear accountability
- Increased launch risk
- Unreliable forecasting
- Limited operational visibility
- Difficulty scaling without adding coordination staff

## Transformation Opportunity

FlowLens will introduce an orchestration and visibility layer across the existing systems.

It will not attempt to replace Salesforce, DocuSign, Jira, NetSuite, Slack, or departmental expertise.

Instead, FlowLens will:

- Create a canonical launch record
- Normalize workflow statuses
- Coordinate cross-functional handoffs
- Track approval decisions
- Assign ownership and due dates
- Detect stalled or at-risk work
- Maintain an audit history
- Provide current operational reporting
- Preserve links to each system of record
- Support automation without hiding human decisions

## Proposed FlowLens Capabilities

### System Landscape

A visual inventory of the systems participating in the workflow, including ownership, responsibilities, dependencies, and known integration gaps.

### Workflow Control Center

A centralized view of every active customer launch, its current stage, responsible owner, outstanding requirements, approvals, and blockers.

### Rules and Routing

Configurable business rules that determine required approvals, assignments, and process steps based on contract and customer attributes.

### Exception Management

Explicit detection and management of missing information, overdue work, conflicting statuses, failed integrations, and blocked launches.

### Audit History

A chronological record of workflow events, ownership changes, approvals, exceptions, and status transitions.

### Transformation Dashboard

Operational reporting that compares current performance with the defined future-state targets.

## Project Objectives

FlowLens must demonstrate the ability to:

1. Analyze an existing multi-system workflow.
2. Distinguish valuable capabilities from process failures.
3. Translate stakeholder needs into structured requirements.
4. Design a future state without unnecessary system replacement.
5. Create an integration-ready data model.
6. Automate repeatable coordination work.
7. Preserve appropriate human review and approval.
8. Detect and communicate operational exceptions.
9. Produce measurable and auditable process outcomes.
10. Support testing, rollout, documentation, and future improvement.

## Target Outcomes

The following are fictional transformation targets used to evaluate the proposed design:

| Measure | Current-State Estimate | Future-State Target |
|---|---:|---:|
| Average contract-to-launch cycle time | 18 business days | 12 business days or fewer |
| Manual data-entry touchpoints per launch | 14 | 5 or fewer |
| Launches with an unclear owner | 22% | Less than 3% |
| Approvals completed outside the tracked workflow | 47% | Less than 5% |
| At-risk launches identified before the target date | 31% | At least 90% |
| Time required to prepare weekly reporting | 4 hours | Less than 15 minutes |

All figures are synthetic and exist only to demonstrate requirements analysis and solution measurement. They do not represent an actual company.

## In Scope

- Current-state analysis
- Stakeholder analysis
- Systems inventory
- Process and data-flow mapping
- Future-state design
- Canonical launch records
- Workflow stages and business rules
- Ownership and assignment
- Approval tracking
- Exception detection
- Audit history
- Operational dashboards
- Simulated system integrations
- Automated testing
- Technical and operational documentation
- UAT and rollout planning

## Out of Scope

- Real Salesforce, DocuSign, Jira, NetSuite, Gmail, or Slack credentials
- Production customer data
- Employer or proprietary information
- Replacement of external systems of record
- Real contract or financial processing
- Production deployment during the initial release
- Machine-learning recommendations
- Mobile applications

## Guiding Principles

1. Preserve what works.
2. Fix the process before automating it.
3. Maintain clear systems of record.
4. Make ownership explicit.
5. Treat exceptions as first-class workflow objects.
6. Keep business rules explainable.
7. Preserve human accountability.
8. Design for auditability.
9. Measure operational outcomes.
10. Use only synthetic data.