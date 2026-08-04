export type WorkStatus = 'On track' | 'At risk' | 'Blocked'

export type WorkItem = {
  id: string
  name: string
  stage: string
  owner: string
  target: string
  status: WorkStatus
  nextAction: string
  updated: string
}

export const workItems: WorkItem[] = [
  { id: 'NS-1042', name: 'Redwood Realty', stage: 'Readiness', owner: 'Maya Chen', target: 'Sep 15', status: 'At risk', nextAction: 'Confirm billing account', updated: '18 minutes ago' },
  { id: 'NS-1047', name: 'Lakeview Group', stage: 'Approval', owner: 'Jordan Lee', target: 'Sep 18', status: 'On track', nextAction: 'Record finance approval', updated: '42 minutes ago' },
  { id: 'NS-1051', name: 'Northwind Partners', stage: 'Validation', owner: 'Avery Brooks', target: 'Sep 22', status: 'Blocked', nextAction: 'Resolve contract mismatch', updated: '1 hour ago' },
  { id: 'NS-1054', name: 'Summit Property Co.', stage: 'Review', owner: 'Maya Chen', target: 'Sep 27', status: 'On track', nextAction: 'Complete legal review', updated: '2 hours ago' },
  { id: 'NS-1058', name: 'Brightline Advisors', stage: 'Intake', owner: 'Chris Morgan', target: 'Oct 02', status: 'At risk', nextAction: 'Assign implementation owner', updated: '3 hours ago' },
  { id: 'NS-1062', name: 'Harbor Point Group', stage: 'Launch', owner: 'Jordan Lee', target: 'Oct 05', status: 'On track', nextAction: 'Confirm launch completion', updated: 'Yesterday' },
]

export const approvals = [
  { id: 'APR-201', item: 'Lakeview Group', type: 'Finance approval', approver: 'Morgan Reed', requested: 'Today, 9:12 AM', status: 'Pending' },
  { id: 'APR-198', item: 'Redwood Realty', type: 'Legal approval', approver: 'Taylor James', requested: 'Yesterday', status: 'Overdue' },
  { id: 'APR-194', item: 'Summit Property Co.', type: 'Contract review', approver: 'Taylor James', requested: 'Aug 2', status: 'Approved' },
]

export const exceptions = [
  { id: 'EXC-091', item: 'Northwind Partners', severity: 'Critical', title: 'Billing account not ready', owner: 'Finance Operations', age: '2d 4h' },
  { id: 'EXC-088', item: 'Redwood Realty', severity: 'High', title: 'Legal approval overdue', owner: 'Legal Operations', age: '18h' },
  { id: 'EXC-085', item: 'Brightline Advisors', severity: 'High', title: 'Owner action overdue', owner: 'Implementation', age: '7h' },
]

export const auditEvents = [
  { event: 'owner_assigned', item: 'Brightline Advisors', actor: 'Workflow rule', time: '10:42 AM' },
  { event: 'approval_requested', item: 'Lakeview Group', actor: 'Jordan Lee', time: '9:12 AM' },
  { event: 'risk_detected', item: 'Redwood Realty', actor: 'Risk engine', time: '8:57 AM' },
  { event: 'stage_completed', item: 'Summit Property Co.', actor: 'Maya Chen', time: 'Yesterday' },
]
