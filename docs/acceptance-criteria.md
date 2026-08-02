# FlowLens Acceptance Criteria

## Document Purpose

This document defines testable acceptance criteria for the initial FlowLens release.

The criteria translate business and system requirements into observable behavior using Given, When, and Then scenarios.

These scenarios will later support:

- Automated testing
- User acceptance testing
- Requirements traceability
- Release-readiness review
- Demonstration planning

## Acceptance-Criteria Conventions

Each scenario includes:

- A unique acceptance-criteria identifier
- Related requirement identifiers
- A priority
- A testable business outcome

### Scenario Terms

- **Given:** The starting context
- **When:** The triggering action or event
- **Then:** The expected result
- **And:** An additional condition or result

## Launch Record Acceptance Criteria

### AC-001: Create Canonical Launch from Valid Handoff

**Related requirements:** FR-001, FR-003, FR-004, IR-002, IR-003  
**Priority:** Must

```gherkin
Given a valid simulated Salesforce closed-won event
And the event contains all required handoff fields
And no launch exists for the source opportunity
When FlowLens processes the event
Then one canonical launch record is created
And the Salesforce opportunity reference is preserved
And the launch enters the Handoff Review stage
And the launch receives an accountable owner
And a launch_created audit event is recorded
```

### AC-002: Reject Incomplete Handoff

**Related requirements:** FR-006, BR-002, IR-003, IR-004  
**Priority:** Must

```gherkin
Given a simulated closed-won event is missing a required handoff field
When FlowLens validates the event
Then no launch record is created
And the response identifies each missing field
And no workflow stage transition occurs
And the invalid event result is recorded
```

### AC-003: Prevent Duplicate Launch

**Related requirements:** FR-002, BR-001, BR-013, IR-005  
**Priority:** Must

```gherkin
Given a launch already exists for a Salesforce opportunity
When FlowLens receives the same external event again
Then a second launch is not created
And duplicate assignments are not created
And duplicate approvals are not created
And the repeated event is recorded as already processed
```

### AC-004: Display Complete Launch Summary

**Related requirements:** FR-004  
**Priority:** Must

```gherkin
Given an authorized user opens an active launch
When the launch summary loads
Then the current workflow stage is displayed
And the accountable owner is displayed
And the next action is displayed
And the target launch date is displayed
And required approvals are displayed
And open exceptions and risks are displayed
And external system references are displayed
```

## Workflow Acceptance Criteria

### AC-005: Prevent Invalid Stage Entry

**Related requirements:** FR-005, FR-006  
**Priority:** Must

```gherkin
Given a launch does not satisfy the entry criteria for Financial Readiness
When a user or automated process attempts to enter Financial Readiness
Then the stage transition is rejected
And the unmet criteria are displayed
And the current stage remains unchanged
And the rejected transition attempt is recorded
```

### AC-006: Prevent Invalid Stage Exit

**Related requirements:** FR-007, BR-003, BR-004, BR-005  
**Priority:** Must

```gherkin
Given a launch is in Launch Approval
And one or more required approvals are incomplete
When an authorized user attempts to advance the launch
Then the transition is rejected
And each incomplete approval is displayed
And the launch remains in Launch Approval
```

### AC-007: Record Valid Stage Transition

**Related requirements:** FR-008, FR-028, FR-029  
**Priority:** Must

```gherkin
Given a launch satisfies all stage-exit criteria
And the launch satisfies all next-stage entry criteria
When an authorized transition occurs
Then the launch enters the next stage
And a stage_completed event is recorded for the previous stage
And a stage_entered event is recorded for the new stage
And the actor, timestamp, reason, and correlation identifier are preserved
```

### AC-008: Pause Customer Launch

**Related requirements:** FR-009  
**Priority:** Must

```gherkin
Given an active launch
When an authorized user applies a customer-requested pause
Then the launch is marked as paused
And the pause reason is required
And the decision-maker and timestamp are recorded
And the user selects whether the target date should be recalculated
And the pause is excluded from internal delay calculations when appropriate
```

### AC-009: Cancel Launch without Deleting History

**Related requirements:** FR-010  
**Priority:** Must

```gherkin
Given an active launch with existing workflow history
When an authorized user cancels the launch
Then the launch is removed from active workflow queues
And the cancellation reason is recorded
And a launch_canceled event is created
And all previous workflow history remains available
```

## Ownership and Assignment Acceptance Criteria

### AC-010: Require Accountable Owner

**Related requirements:** FR-011, BR-006  
**Priority:** Must

```gherkin
Given an active launch
When FlowLens evaluates ownership
Then exactly one accountable owner exists
And the owner is active
And the owner is authorized for the assigned responsibility
```

### AC-011: Require Next Action

**Related requirements:** FR-012  
**Priority:** Must

```gherkin
Given an active launch
When FlowLens evaluates the current stage
Then at least one explicit next action exists
And the action has a responsible party
And the action has a due date when required
```

### AC-012: Apply Explainable Routing Rule

**Related requirements:** FR-013, NFR-010  
**Priority:** Must

```gherkin
Given a launch enters a stage with a defined routing rule
When FlowLens assigns ownership
Then the expected owner or role is assigned
And the rule responsible for the assignment is available
And an owner_assigned event is recorded
```

### AC-013: Audit Reassignment

**Related requirements:** FR-014  
**Priority:** Must

```gherkin
Given an authorized user reassigns an active launch or task
When the reassignment is saved
Then the previous owner is preserved
And the new owner is displayed
And the actor, timestamp, and reason are recorded
And an owner_changed event is created
```

### AC-014: Detect Overdue Assignment

**Related requirements:** FR-015, KPI-13  
**Priority:** Must

```gherkin
Given an incomplete assignment has passed its due time
When the overdue evaluation runs
Then the assignment is marked overdue within 15 minutes
And a visible exception is created
And the exception has an accountable owner
And the launch risk status is recalculated
```

## Approval Acceptance Criteria

### AC-015: Create Structured Approval Request

**Related requirements:** FR-016  
**Priority:** Must

```gherkin
Given a launch enters a stage requiring specialist approval
When FlowLens creates the approval request
Then the request identifies the launch
And the approval type is displayed
And the assigned decision-maker or role is displayed
And the required context is available
And an approval_requested event is recorded
```

### AC-016: Record Approval Decision

**Related requirements:** FR-017, FR-018  
**Priority:** Must

```gherkin
Given an authorized specialist has an open approval request
When the specialist submits a valid decision
Then the decision is recorded
And the decision-maker is recorded
And the timestamp is recorded
And the workflow stage is recorded
And the reason or conditions are required when applicable
And an approval_decided event is created
```

### AC-017: Prevent Inferred Approval

**Related requirements:** FR-019, FR-037, BR-003, BR-004  
**Priority:** Must

```gherkin
Given a required approval remains pending
When time passes or a related task is completed
Then the approval remains pending
And the launch cannot advance through an approval-gated stage
And no approval_decided event is created
```

### AC-018: Rejected Approval Creates Exception

**Related requirements:** BR-008, FR-021, FR-023  
**Priority:** Must

```gherkin
Given an authorized specialist rejects an approval request
When the decision is submitted
Then the approval is marked rejected
And an assigned exception is created
And the launch is marked blocked when required
And the rejection reason is visible
```

### AC-019: More Information Required Creates Action

**Related requirements:** BR-009, FR-012  
**Priority:** Must

```gherkin
Given an authorized specialist selects More Information Required
When the decision is submitted
Then a next action is created
And an accountable owner is assigned
And the required information is described
And the approval remains incomplete
```

### AC-020: Preserve Approval Conditions

**Related requirements:** BR-010  
**Priority:** Must

```gherkin
Given an approval is granted with conditions
When the launch progresses
Then the conditions remain visible
And each condition has a completion state
And unmet required conditions prevent final approval
And a condition cannot disappear without an audit event
```

## Exception and Risk Acceptance Criteria

### AC-021: Create Complete Exception

**Related requirements:** FR-021, FR-022, FR-023  
**Priority:** Must

```gherkin
Given a workflow rule detects a blocker or failure
When an exception is created
Then it contains an exception type
And it contains a severity
And it contains a description
And it references the affected launch and stage
And it has an accountable owner
And it records its creation time
```

### AC-022: Resolve Exception with Evidence

**Related requirements:** FR-024  
**Priority:** Must

```gherkin
Given an authorized user resolves an open exception
When the resolution is submitted
Then the resolution explanation is required
And the responsible actor is recorded
And the resolution timestamp is recorded
And an exception_resolved event is created
And the launch risk status is recalculated
```

### AC-023: Critical Exception Blocks Completion

**Related requirements:** FR-025, BR-007, GR-02  
**Priority:** Must

```gherkin
Given a launch has an unresolved critical exception
When a user attempts to approve or complete the launch
Then the action is rejected
And the critical exception is displayed
And no launch_completed event is created
```

### AC-024: Detect At-Risk Launch

**Related requirements:** FR-026, KPI-05  
**Priority:** Must

```gherkin
Given a launch has an approaching target date
And required work is overdue or incomplete
When FlowLens evaluates launch risk
Then the launch is marked at risk
And a risk_detected event is recorded
And the responsible condition is displayed
And the accountable owner is notified
```

### AC-025: Explain Risk Status

**Related requirements:** FR-027, NFR-010  
**Priority:** Must

```gherkin
Given a launch is marked at risk or blocked
When a user views the launch
Then each contributing rule or exception is displayed
And the user can navigate to the related assignment, approval, or exception
```

## Audit Acceptance Criteria

### AC-026: Preserve Append-Only History

**Related requirements:** FR-028, BR-015  
**Priority:** Must

```gherkin
Given a launch has recorded workflow events
When its current state changes
Then previous events remain unchanged
And new events are appended to the history
And normal application users cannot edit or delete historical events
```

### AC-027: Capture Required Audit Fields

**Related requirements:** FR-029, DR-001, DR-005, KPI-12  
**Priority:** Must

```gherkin
Given a material workflow action occurs
When the audit event is stored
Then it contains a unique event identifier
And it references the launch
And it identifies the event type
And it uses a UTC timestamp
And it identifies the actor or source system
And it contains a correlation identifier
And it records previous and new state when applicable
And it contains a reason when required
```

### AC-028: Display Chronological Launch Timeline

**Related requirements:** FR-030  
**Priority:** Must

```gherkin
Given an authorized user opens a launch timeline
When the event history loads
Then events are displayed chronologically
And assignments are identifiable
And approvals are identifiable
And stage transitions are identifiable
And exceptions and risks are identifiable
And integration activity is identifiable
```

## Integration Acceptance Criteria

### AC-029: Process Valid External Event

**Related requirements:** IR-001, IR-002, IR-003, IR-006  
**Priority:** Must

```gherkin
Given a supported simulated external event
And the event contains valid data
When FlowLens receives the event
Then the event is marked received
And the event is processed
And the corresponding workflow action occurs
And the event is marked processed
And the correlation identifier is preserved
```

### AC-030: Reject Invalid External Event Safely

**Related requirements:** IR-003, IR-004  
**Priority:** Must

```gherkin
Given an external event contains invalid or unsupported data
When FlowLens validates the event
Then the event does not change workflow state
And an explainable validation error is returned
And the failed validation is recorded
```

### AC-031: Process Duplicate Event Idempotently

**Related requirements:** BR-013, IR-005, NFR-003, GR-05  
**Priority:** Must

```gherkin
Given an external event has already been processed
When the same event identifier is received again
Then no duplicate workflow action occurs
And no duplicate audit action occurs
And the response identifies the event as previously processed
```

### AC-032: Create Visible Integration Failure

**Related requirements:** BR-014, IR-007, NFR-002, NFR-004, GR-07  
**Priority:** Must

```gherkin
Given a valid integration event cannot be processed
And all permitted retry attempts have failed
When the event reaches its final failure state
Then an integration_failed event is recorded
And a visible integration exception is created
And the exception has an accountable owner
And the failure does not exist only in application logs
```

## Operational View Acceptance Criteria

### AC-033: Filter Active Launches

**Related requirements:** FR-031, FR-032  
**Priority:** Must

```gherkin
Given multiple active launches exist
When an authorized user applies one or more supported filters
Then only matching launches are displayed
And the active filters are visible
And the result count is updated
```

### AC-034: Search Launches

**Related requirements:** FR-033  
**Priority:** Must

```gherkin
Given a launch exists
When a user searches using its launch identifier, customer name, external identifier, or contract reference
Then the matching launch is returned
```

### AC-035: Display Personal Work Queue

**Related requirements:** FR-034  
**Priority:** Must

```gherkin
Given an authenticated user owns active work
When the user opens the work queue
Then owned assignments are displayed
And pending approvals are displayed
And owned exceptions are displayed
And overdue work is clearly identified
```

## Dashboard Acceptance Criteria

### AC-036: Display Operational Summary

**Related requirements:** RR-001  
**Priority:** Must

```gherkin
Given synthetic launch data exists
When an authorized user opens the dashboard
Then active launch totals are displayed
And stage distribution is displayed
And on-track, at-risk, and blocked totals are displayed
And overdue assignments are displayed
And pending approvals are displayed
And open exceptions are displayed
And upcoming target dates are displayed
```

### AC-037: Calculate Metrics from Event History

**Related requirements:** RR-002, KPI-01 through KPI-14  
**Priority:** Must

```gherkin
Given a defined synthetic workflow dataset
When dashboard measures are calculated
Then each measure uses its documented formula
And the result can be reproduced from stored workflow events
And canceled and paused launches are handled according to the measurement rules
```

### AC-038: Label Synthetic Results

**Related requirements:** RR-003, NFR-018  
**Priority:** Must

```gherkin
Given the dashboard displays project demonstration results
When a user views a measure
Then current-state estimates are identified
And future-state targets are identified
And simulated FlowLens results are identified
And no simulated result is represented as an actual business outcome
```

## Security and Authorization Acceptance Criteria

### AC-039: Restrict Protected Capabilities

**Related requirements:** NFR-005, NFR-006, NFR-007  
**Priority:** Must

```gherkin
Given a user lacks permission for a protected action
When the user attempts the action
Then access is denied
And workflow state remains unchanged
And the denied action is recorded when required
```

### AC-040: Limit Sensitive Information

**Related requirements:** NFR-008  
**Priority:** Must

```gherkin
Given a user can view general launch status
But the user lacks access to restricted decision details
When the launch summary loads
Then the general workflow status is visible
And restricted contract or financial details are not exposed
```

### AC-041: Audit Authorized Override

**Related requirements:** BR-011, BR-012  
**Priority:** Must

```gherkin
Given an authorized user overrides a workflow rule
When the override is submitted
Then a reason is required
And the affected rule is recorded
And the previous and resulting states are recorded
And the actor and timestamp are recorded
And an audit event is created
```

## Accessibility Acceptance Criteria

### AC-042: Support Keyboard Navigation

**Related requirements:** NFR-011  
**Priority:** Must

```gherkin
Given a user navigates without a mouse
When the user moves through an operational view
Then every interactive control can receive keyboard focus
And the focus order is logical
And the visible focus state is clear
And the user can activate the control with the keyboard
```

### AC-043: Provide Semantic Labels

**Related requirements:** NFR-011  
**Priority:** Must

```gherkin
Given a user accesses FlowLens with assistive technology
When a form, table, status, or interactive control is presented
Then the content has an appropriate semantic structure
And controls have descriptive labels
And status is not communicated by color alone
```

## Privacy Acceptance Criteria

### AC-044: Use Only Synthetic Data

**Related requirements:** DR-006, NFR-018, GR-08  
**Priority:** Must

```gherkin
Given the repository, application, demonstration data, screenshots, and reports
When project content is reviewed
Then no real customer information is present
And no employer data is present
And no proprietary workflow is present
And no production credential is present
And all demonstration records are fictional
```

## Initial Release Acceptance

The initial FlowLens release is acceptable only when:

- Every Must acceptance criterion has a passing automated test, passing UAT scenario, or documented verification method.
- No unresolved critical defect remains.
- No guardrail requirement is violated.
- Requirement-to-test traceability is complete.
- Synthetic data labeling is visible.
- Known limitations are documented.
- The application behavior matches the documented future-state workflow.