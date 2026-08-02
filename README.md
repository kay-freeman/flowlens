# FlowLens

**Status: Discovery and Current-State Analysis**

FlowLens is a business systems transformation platform designed to map fragmented workflows, identify operational friction, preserve the systems and practices that already work, and model a measurable future state.

Rather than replacing every existing tool, FlowLens demonstrates how a systems analyst can evaluate an organization’s people, processes, systems, data, decisions, and handoffs before designing an improved operating model.

## The Project

FlowLens uses a fictional company, Northstar Business Services, to demonstrate an end-to-end systems transformation engagement.

Northstar’s contract-to-launch workflow crosses Sales, Legal, Finance, Implementation, Operations, and Executive Leadership. The process currently depends on disconnected systems, spreadsheet tracking, email approvals, Slack updates, duplicated data entry, and manual coordination.

The existing tools perform many of their individual responsibilities well. The larger failure occurs between those tools, where workflow state, ownership, decisions, and exceptions become fragmented.

FlowLens will become the orchestration and intelligence layer across that environment.

## Business Problem

Northstar’s contract-to-launch process currently spans:

- Salesforce for customer and opportunity data
- DocuSign for executed contracts
- Gmail for Legal and Finance approvals
- Google Sheets for launch tracking
- Slack for internal coordination
- Jira for implementation work
- NetSuite for billing readiness

No single system provides a complete, reliable view of the workflow.

This creates:

- Duplicate data entry
- Conflicting status information
- Invisible or delayed approvals
- Unclear ownership between departments
- Weak handoffs
- Late discovery of blockers
- Manual leadership reporting
- Limited auditability
- Process knowledge that depends on individual coordinators

## Transformation Approach

FlowLens follows a systems-analysis-first approach:

1. Understand the business problem.
2. Inventory the existing systems.
3. Map the current workflow and data movement.
4. Identify root causes instead of treating symptoms.
5. Preserve the capabilities that already work.
6. Define stakeholder and business requirements.
7. Design the future-state process and architecture.
8. Build an orchestration and visibility platform.
9. Validate the solution through testing and UAT.
10. Measure the proposed operational improvement.

## What FlowLens Will Provide

### System Landscape

A visual inventory of the systems participating in the workflow, including ownership, responsibilities, dependencies, and integration gaps.

### Workflow Control Center

A centralized view of active customer launches, workflow stages, owners, approvals, requirements, blockers, and due dates.

### Rules and Routing

Explainable business rules that determine required approvals, assignments, and workflow paths.

### Exception Management

Structured detection and tracking for missing information, overdue work, conflicting statuses, failed integrations, and blocked launches.

### Audit History

A chronological record of status transitions, ownership changes, approvals, exceptions, and other workflow events.

### Transformation Dashboard

Operational reporting that compares the fragmented current state with clearly defined future-state targets.

## Design Principles

FlowLens is guided by the following principles:

- Preserve what works.
- Fix the process before automating it.
- Maintain clear systems of record.
- Make ownership explicit.
- Treat exceptions as first-class workflow objects.
- Keep business rules explainable.
- Preserve human accountability.
- Design for auditability.
- Measure operational outcomes.
- Use only synthetic data.

## Current-State Findings

The initial analysis identified several root-cause themes:

### Fragmented Workflow State

Each system represents only part of the process. No reliable record of the overall launch lifecycle exists.

### Unstructured Decisions

Important Legal, Finance, and readiness decisions occur in communication channels without becoming structured workflow data.

### Manual Reconciliation

Coordinators must compare multiple systems and determine which information is current.

### Implicit Ownership

Responsibility depends on experience and conversation rather than explicit assignments and handoff rules.

### Reactive Exception Management

Missing information and stalled work are often discovered only after a launch date becomes threatened.

### Reporting Without Event History

The current spreadsheet captures an interpreted status but not the complete history that produced it.

## Target Outcomes

The following targets are fictional and are used to evaluate the proposed design:

| Measure | Current-State Estimate | Future-State Target |
|---|---:|---:|
| Average contract-to-launch cycle time | 18 business days | 12 business days or fewer |
| Manual data-entry touchpoints per launch | 14 | 5 or fewer |
| Launches with an unclear owner | 22% | Less than 3% |
| Approvals completed outside the tracked workflow | 47% | Less than 5% |
| At-risk launches identified before the target date | 31% | At least 90% |
| Time required to prepare weekly reporting | 4 hours | Less than 15 minutes |

All figures are synthetic. They do not represent an actual company, employer, customer, or production environment.

## Documentation

The repository currently includes the following systems-analysis artifacts:

- [Business Case](docs/business-case.md)  
  Defines the fictional organization, business problem, project scope, transformation opportunity, and target outcomes.

- [Current-State Analysis](docs/current-state.md)  
  Maps the existing systems, workflow, data movement, manual touchpoints, pain points, root causes, constraints, and capabilities that must be preserved.

Additional stakeholder, requirements, architecture, data-model, testing, and rollout documentation will be added as the project progresses.

## Project Roadmap

### Phase 1: Discovery and Analysis

- [x] Define the fictional organization and business problem
- [x] Document the current system landscape
- [x] Map the current contract-to-launch workflow
- [x] Analyze current data movement
- [x] Create the pain-point register
- [x] Identify root-cause themes
- [ ] Define stakeholder needs and responsibilities
- [ ] Establish detailed success measures

### Phase 2: Requirements and Future State

- [ ] Define functional requirements
- [ ] Define nonfunctional requirements
- [ ] Create acceptance criteria
- [ ] Build the requirements traceability matrix
- [ ] Design the future-state workflow
- [ ] Define system boundaries
- [ ] Document integration contracts
- [ ] Create the canonical data model

### Phase 3: Platform Development

- [ ] Build the FlowLens application foundation
- [ ] Implement canonical launch records
- [ ] Implement workflow stages and transitions
- [ ] Implement ownership and assignments
- [ ] Implement approval tracking
- [ ] Implement exception detection
- [ ] Implement audit history
- [ ] Build the system-landscape view
- [ ] Build the workflow control center
- [ ] Build the transformation dashboard

### Phase 4: Quality and Delivery

- [ ] Add automated tests
- [ ] Configure continuous integration
- [ ] Create synthetic demonstration data
- [ ] Execute UAT scenarios
- [ ] Document release and rollout strategy
- [ ] Document limitations and future enhancements
- [ ] Publish the first formal release
- [ ] Add FlowLens to the portfolio website

## Repository Structure

```text
flowlens/
├── docs/
│   ├── business-case.md
│   └── current-state.md
├── LICENSE
└── README.md
```

The structure will expand as requirements, architecture, application code, tests, and deployment configuration are introduced.

## Privacy and Data

FlowLens is a fictional portfolio project.

The repository will not contain:

- Real customer information
- Employer data
- Proprietary workflows
- Production credentials
- Real contracts
- Real financial records
- Private API keys

All organizations, users, records, metrics, and integrations will be simulated.

## Why This Project Exists

FlowLens is designed to demonstrate more than software development.

It demonstrates the ability to:

- Understand a complex business environment
- Analyze systems and operational workflows
- Separate symptoms from root causes
- Preserve valuable existing capabilities
- Translate stakeholder needs into requirements
- Design integrations and future-state processes
- Build reliable and explainable automation
- Plan testing, rollout, measurement, and adoption
- Communicate technical decisions clearly

The objective is not merely to build another application.

The objective is to show how a fragmented operating model can be understood, redesigned, implemented, and improved.