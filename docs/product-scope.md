# FlowLens Product Scope

## Document Purpose

This document defines FlowLens as a reusable, self-hostable workflow-transformation platform.

It distinguishes the core product from the fictional Northstar Business Services demonstration and establishes what “usable” means for the initial release.

## Product Decision

FlowLens will not be built as a hardcoded application that supports only Northstar’s contract-to-launch process.

FlowLens will be built as:

> A self-hostable workflow-orchestration platform that allows an organization to model cross-functional work, define ownership and approvals, manage exceptions, preserve audit history, and measure process performance.

Northstar’s contract-to-launch workflow will be included as a complete demonstration template.

## Product and Demonstration Separation

### FlowLens Core

The core product provides reusable capabilities:

- Organization configuration
- Workflow templates
- Configurable stages
- Work-item records
- Assignments
- Approvals
- Requirements
- Exceptions
- Risk rules
- Audit events
- Generic event intake
- Operational dashboards
- Role-based experiences

### Northstar Demonstration

The Northstar demonstration provides:

- A fictional organization
- Synthetic users and roles
- A contract-to-launch workflow template
- Synthetic external-system events
- Sample work items
- Approval scenarios
- Exception scenarios
- Dashboard history
- Before-and-after transformation targets

The demonstration proves the platform’s capabilities without becoming the platform’s only supported use case.

## Product Positioning

FlowLens is designed for organizations whose important work is distributed across:

- Multiple departments
- Multiple software systems
- Manual handoffs
- Spreadsheet trackers
- Email approvals
- Chat-based status updates
- Unclear ownership
- Inconsistent reporting

FlowLens provides an orchestration and visibility layer without requiring every existing system to be replaced.

## Intended Users

### Organization Administrator

Configures the FlowLens deployment, users, roles, organization settings, and integration access.

### Workflow Designer

Creates and maintains workflow templates, stages, requirements, approvals, routing rules, and SLA policies.

### Process Owner

Owns the end-to-end business outcome and monitors process performance.

### Operator

Coordinates active work items, manages assignments, and resolves process exceptions.

### Contributor

Completes assigned actions and supplies required information.

### Approver

Makes structured decisions within an authorized area of responsibility.

### Auditor

Reviews workflow history, approvals, overrides, and control evidence.

### Viewer

Receives read-only access to permitted workflow and reporting information.

## Core Product Concepts

## Organization

An `Organization` represents one company or operating environment using a FlowLens deployment.

The initial release supports one active organization per deployment.

## Workflow Template

A `WorkflowTemplate` defines a reusable business process.

A template contains:

- Name and description
- Version
- Stages
- Stage order
- Entry criteria
- Exit criteria
- Requirements
- Approval definitions
- Assignment rules
- SLA rules
- Risk rules
- Notification rules
- Active or draft status

## Work Item

A `WorkItem` is one instance of a workflow template.

Examples include:

- Customer launch
- Vendor onboarding
- Employee access request
- Procurement review
- Product release
- Compliance assessment
- Contract renewal
- Internal change request

The Northstar demonstration uses a customer launch as its work-item type.

## Workflow Stage

A `WorkflowStage` defines one controlled step in a workflow template.

Each stage may specify:

- Default owner or role
- Required fields
- Required actions
- Required approvals
- Entry criteria
- Exit criteria
- SLA target
- Risk thresholds
- Allowed transitions

## Assignment

An `Assignment` represents an explicit action owned by a user or role.

## Approval

An `Approval` represents a structured decision that must be made by an authorized user or role.

## Requirement

A `Requirement` represents information, evidence, or completion criteria needed by a work item.

## Exception

An `Exception` represents a blocker, failure, conflict, or policy deviation requiring investigation or resolution.

## Workflow Event

A `WorkflowEvent` preserves append-only history explaining how a work item reached its current state.

## Integration Event

An `IntegrationEvent` represents data received from, or sent to, another system.

## Metric Definition

A `MetricDefinition` describes how a process measure is calculated from workflow data.

## Initial Release Capabilities

## Installation and Setup

A user must be able to:

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Start FlowLens with Docker Compose.
4. Apply database migrations.
5. Create or load the initial organization.
6. Open the application in a browser.
7. Use the Northstar demonstration or configure a workflow.

The project must document each step.

## Organization Management

An administrator must be able to:

- Configure the organization name
- Set a default timezone
- View organization status
- Manage synthetic or configured users
- Assign roles
- Review active workflow templates

The initial release supports one organization per deployment.

## Workflow Configuration

An authorized workflow designer must be able to:

- Create a workflow template
- Create stages
- Define stage order
- Assign default stage roles
- Define required fields
- Define stage requirements
- Define required approvals
- Define entry and exit criteria
- Configure SLA targets
- Activate a workflow-template version
- Preserve previous versions for existing work

## Work-Item Intake

The initial release must support:

- Manual work-item creation
- CSV import
- REST API creation
- Generic webhook creation
- Northstar Salesforce demonstration events

Each intake method must use the same domain services and validation rules.

## Work Management

Users must be able to:

- View active work items
- Search and filter work items
- Open a work-item summary
- View the current stage
- View accountable ownership
- View and complete assignments
- View and complete requirements
- Submit approval decisions
- Create and resolve exceptions
- View calculated risk
- View chronological history

## Operational Reporting

Users must be able to view:

- Active work-item totals
- Work items by stage
- Work items by owner
- On-track, at-risk, blocked, and paused work
- Overdue assignments
- Pending approvals
- Open exceptions
- Workflow cycle time
- Template-specific metrics

## Integration Foundation

The initial release must provide:

- Generic event envelope
- Generic inbound webhook
- REST API
- CSV import
- Idempotency handling
- Processing lifecycle
- Retry behavior
- Visible integration failures
- Adapter interface
- Northstar demonstration adapters

## Auditability

The initial release must record:

- Work-item creation
- Stage transitions
- Ownership changes
- Assignment changes
- Approval decisions
- Requirement completion or waiver
- Exception creation and resolution
- Risk changes
- Integration processing
- Overrides
- Cancellation
- Completion

## Product Modes

## Demonstration Mode

Demonstration mode provides:

- Seeded Northstar organization
- Synthetic users
- Demo persona selection
- Synthetic data
- Simulated connectors
- Resettable demonstration state

Demonstration mode must be visibly identified as nonproduction.

## Configured Deployment Mode

Configured deployment mode provides:

- Persistent organization configuration
- Real user identity through the selected authentication approach
- Role-based authorization
- Custom workflow templates
- Manual, CSV, API, and webhook intake
- Persistent PostgreSQL storage
- Environment-based configuration
- Deployment documentation

The project must not describe configured deployment mode as production-ready until its security, backup, recovery, and deployment limitations are documented and tested.

## Definition of Usable

FlowLens is considered usable when a person unfamiliar with the source code can:

1. Follow the documented installation process.
2. Start the complete platform.
3. Sign in or enter clearly labeled demonstration mode.
4. Load the included Northstar template.
5. Create a work item.
6. Move the work item through valid stages.
7. Observe an invalid transition being blocked.
8. Complete an assignment.
9. Record an approval decision.
10. Create and resolve an exception.
11. View the audit timeline.
12. View dashboard changes.
13. Import work items through CSV.
14. submit a work item through the REST API or webhook.
15. Shut down and restart without losing persistent data.

## Definition of Configurable

FlowLens is considered configurable when an authorized user can create a workflow without changing application source code.

At minimum, the user must be able to configure:

- Workflow name
- Work-item label
- Workflow description
- Stage names
- Stage order
- Default stage owner roles
- Required fields
- Required approvals
- SLA values
- Basic entry and exit rules
- Risk thresholds

Advanced custom-code rules are outside the initial release.

## Definition of Self-Hostable

FlowLens is considered self-hostable when:

- The repository contains all required application source.
- Docker Compose starts required services.
- Required environment variables are documented.
- Database migrations are automated or clearly documented.
- Health checks are available.
- Persistent volumes are configured.
- Setup does not require proprietary deployment tooling.
- External services are optional for demonstration mode.
- Backup and restoration procedures are documented.
- Upgrade limitations are documented.

## Northstar Template Mapping

| Northstar Concept | Generic FlowLens Concept |
|---|---|
| Contract-to-launch process | Workflow Template |
| Customer launch | Work Item |
| Launch stage | Workflow Stage |
| Operations coordinator | Process Owner or Operator |
| Legal review | Approval Definition |
| Financial readiness | Approval and Requirement |
| Technical readiness | Conditional Approval and Requirements |
| Launch blocker | Exception |
| Target launch date | Work-Item Target Date |
| Salesforce opportunity | External Reference |
| Jira implementation project | External Reference |
| Launch timeline | Workflow Event History |
| Launch dashboard | Template-Specific Dashboard |

## Product Data Model Direction

The reusable model must introduce:

- `Organization`
- `WorkflowTemplate`
- `WorkflowTemplateVersion`
- `WorkflowStageDefinition`
- `WorkItem`
- `WorkItemFieldValue`
- `Assignment`
- `ApprovalDefinition`
- `Approval`
- `RequirementDefinition`
- `WorkItemRequirement`
- `Exception`
- `WorkflowEvent`
- `IntegrationEvent`
- `ExternalReference`
- `RiskSnapshot`
- `MetricDefinition`

Northstar-specific labels belong in template configuration and seeded demonstration data rather than core table or service names.

## Configuration Boundaries

The initial release supports configuration through controlled options.

It will not initially support arbitrary user-written code inside workflow rules.

Supported rule types may include:

- Required field present
- Requirement completed
- Approval completed
- No open exception at selected severity
- Assignment completed
- Date threshold reached
- External status equals value
- User has required role
- Previous stage completed

This keeps rules explainable and safely testable.

## Authentication Direction

FlowLens will distinguish between:

### Demo Identity

Seeded personas used only for demonstration and UAT.

### Configured Identity

Authenticated users associated with the deployed organization.

The final authentication implementation must:

- Protect authenticated routes
- Use secure password or identity-provider practices
- Enforce authorization in the backend
- Use secure session handling
- Avoid committing secrets
- Document security limitations
- Prevent demo mode from being mistaken for production security

The exact authentication implementation will be finalized before its vertical slice begins.

## Deployment Deliverables

The repository will include:

- `docker-compose.yml`
- `.env.example`
- Database migration commands
- Seed commands
- Health-check endpoints
- Getting-started guide
- Deployment guide
- Configuration reference
- Backup and restore guide
- Upgrade notes
- Troubleshooting guide
- Security documentation

## Product Documentation Deliverables

Before the first formal release, FlowLens will include:

- Product overview
- Quick-start guide
- Administrator guide
- Workflow-designer guide
- User guide
- API reference
- Webhook reference
- CSV-import reference
- Deployment guide
- Configuration reference
- Security model
- Backup and recovery guide
- Connector-development guide
- Contributing guide
- Known limitations
- Changelog

## Initial Release Non-Goals

The initial release will not provide:

- Multiple organizations in one deployment
- A hosted commercial service
- Mobile applications
- Arbitrary user-written workflow code
- Real Salesforce certification
- Real DocuSign certification
- Real NetSuite certification
- Enterprise identity-provider certification
- Guaranteed high availability
- Production service-level agreements
- Enterprise disaster-recovery guarantees
- Machine-learning workflow recommendations
- A no-code interface for every possible rule type
- Replacement of specialized systems of record

## Product Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Generic workflow scope becomes too large | Project never reaches a usable release | Limit v1 to controlled configuration and one organization |
| Northstar logic leaks into the core | Product is not truly reusable | Keep labels and rules in template configuration |
| Setup requires source-code knowledge | Repository remains only a developer demo | Test installation from a clean environment |
| Demo identity is mistaken for real security | Product capability is overstated | Clearly separate demo and configured modes |
| Configuration becomes arbitrary code | Security and explainability degrade | Support controlled rule types |
| Connectors block product use | Users cannot try their own workflows | Provide manual, CSV, API, and generic webhook intake |
| Documentation arrives too late | Installation and adoption become difficult | Develop setup and user documentation alongside features |
| Product claims exceed verification | Portfolio credibility is reduced | Label implemented, planned, simulated, and production limitations precisely |

## Release Strategy

FlowLens will be delivered through vertical product slices.

### Slice 1: Installable Foundation

- Monorepo
- Web application
- API
- PostgreSQL
- Redis
- Docker Compose
- Health checks
- Environment example
- Continuous integration

### Slice 2: Organization and Workflow Template

- Organization record
- Demo organization
- Workflow template
- Stage configuration
- Northstar template seed

### Slice 3: Work-Item Intake

- Manual creation
- Generic API creation
- Generic webhook
- Canonical validation
- Duplicate prevention

### Slice 4: Workflow Execution

- Stage transitions
- Ownership
- Assignments
- Requirements
- Audit events

### Slice 5: Decisions and Exceptions

- Approvals
- Exceptions
- Risk rules
- Overrides

### Slice 6: Operational Experience

- Work queues
- Search and filters
- Work-item detail
- Timeline
- Dashboard

### Slice 7: Reusable Adoption

- CSV import
- Workflow configuration
- Deployment guide
- Backup and recovery
- Security documentation
- Clean-install verification

## Product Success Criteria

FlowLens will qualify as a reusable initial release when:

1. A clean installation succeeds using documented commands.
2. The complete platform starts through Docker Compose.
3. The Northstar template is available as optional seed data.
4. A user can configure a second workflow without changing source code.
5. Work items can enter through manual, CSV, API, and webhook methods.
6. Workflow stages, assignments, approvals, requirements, and exceptions function.
7. Audit history is preserved.
8. Dashboard measures update from workflow events.
9. Data survives restart.
10. Automated tests cover critical business rules.
11. Demo and configured modes are clearly separated.
12. Known production limitations are documented.
13. The repository contains no real credentials or proprietary data.

## Product Scope Conclusion

FlowLens will be both a systems-transformation case study and a reusable software product.

Northstar demonstrates how the platform solves a complex fragmented workflow.

The configurable core, documented installation, generic intake methods, persistent data, and deployment guidance ensure that another person can use FlowLens for a workflow of their own.