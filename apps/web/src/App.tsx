import { useMemo, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Link, NavLink, Navigate, Route, Routes, useNavigate, useParams } from 'react-router'
import './App.css'
import { approvals, auditEvents, exceptions, workItems, type WorkItem, type WorkStatus } from './data'

const navItems = [
  { to: '/', label: 'Overview', icon: 'OV' },
  { to: '/work-items', label: 'Work items', icon: 'WI', count: 24 },
  { to: '/approvals', label: 'Approvals', icon: 'AP', count: 6 },
  { to: '/exceptions', label: 'Exceptions', icon: 'EX', count: 3, urgent: true },
  { to: '/integrations', label: 'Integrations', icon: 'IN' },
  { to: '/audit', label: 'Audit history', icon: 'AU' },
]

const adminItems = [
  { to: '/templates', label: 'Workflow templates' },
  { to: '/people', label: 'People and roles' },
  { to: '/settings', label: 'Settings' },
]

function StatusBadge({ status }: { status: WorkStatus | string }) {
  return <span className={`status status-${status.toLowerCase().replaceAll(' ', '-')}`}>{status}</span>
}

function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" to="/">
          <span className="brand-mark">FL</span>
          <span><strong>FlowLens</strong><small>Workflow intelligence</small></span>
        </Link>

        <nav className="primary-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <NavLink className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end={item.to === '/'} key={item.to} to={item.to}>
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
              {item.count ? <span className={item.urgent ? 'nav-count urgent' : 'nav-count'}>{item.count}</span> : null}
            </NavLink>
          ))}
        </nav>

        <div className="admin-nav">
          <p>Administration</p>
          {adminItems.map((item) => (
            <NavLink className={({ isActive }) => isActive ? 'admin-link active' : 'admin-link'} key={item.to} to={item.to}>{item.label}</NavLink>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="demo-card"><span></span><div><strong>Demonstration mode</strong><small>Synthetic Northstar data</small></div></div>
          <div className="user-card"><span className="avatar">KF</span><div><strong>Kay Freeman</strong><small>Platform administrator</small></div></div>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  )
}

function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description?: string; actions?: ReactNode }) {
  return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{description ? <p className="page-description">{description}</p> : null}</div>{actions ? <div className="header-actions">{actions}</div> : null}</header>
}

function DemoNotice() {
  return <div className="notice"><span className="notice-icon">i</span><div><strong>Northstar demonstration environment</strong><p>Every person, organization, and result shown here is synthetic.</p></div><Link to="/templates">View template</Link></div>
}

function OverviewPage() {
  const stages = [
    { name: 'Intake', count: 3, percent: 30 }, { name: 'Validation', count: 5, percent: 52 },
    { name: 'Review', count: 4, percent: 42 }, { name: 'Readiness', count: 6, percent: 64 },
    { name: 'Approval', count: 4, percent: 42 }, { name: 'Launch', count: 2, percent: 22 },
  ]
  return <>
    <PageHeader eyebrow="Northstar Business Services" title="Operations overview" description="See ownership, risk, approvals, and workflow movement without reconciling separate systems." actions={<><Link className="button secondary" to="/imports/new">Import CSV</Link><Link className="button primary" to="/work-items/new">New work item</Link></>} />
    <DemoNotice />
    <section className="metric-grid" aria-label="Workflow metrics">
      {[['Active work','24','Across 6 workflow stages','blue'],['On track','17','71% of active work','cyan'],['At risk','5','3 require action today','amber'],['Blocked','2','Critical exceptions open','coral']].map(([label,value,detail,tone]) => <article className={`metric ${tone}`} key={label}><p>{label}</p><strong>{value}</strong><span>{detail}</span></article>)}
    </section>
    <section className="overview-grid">
      <article className="panel stage-panel"><div className="panel-header"><div><p className="eyebrow">Workflow distribution</p><h2>Active work by stage</h2></div><Link to="/work-items">View workflow</Link></div><div className="stage-list">{stages.map((stage) => <div className="stage-row" key={stage.name}><div><span>{stage.name}</span><strong>{stage.count}</strong></div><div className="bar"><span style={{ width: `${stage.percent}%` }} /></div></div>)}</div></article>
      <article className="panel"><div className="panel-header"><div><p className="eyebrow">Needs attention</p><h2>Open exceptions</h2></div><StatusBadge status="3 open" /></div><div className="exception-list">{exceptions.map((exception) => <Link key={exception.id} to="/exceptions"><span className={`severity ${exception.severity.toLowerCase()}`} /><div><small>{exception.severity}</small><strong>{exception.title}</strong><p>{exception.item}</p></div><time>{exception.age}</time></Link>)}</div><Link className="panel-action" to="/exceptions">View all exceptions <span>→</span></Link></article>
    </section>
    <WorkTable items={workItems.slice(0, 4)} title="Priority work items" compact />
  </>
}

function WorkTable({ items, title, compact = false }: { items: WorkItem[]; title: string; compact?: boolean }) {
  return <section className="panel table-panel"><div className="panel-header"><div><p className="eyebrow">Operational queue</p><h2>{title}</h2></div>{compact ? <Link to="/work-items">View all work</Link> : null}</div><div className="table-scroll"><table><thead><tr><th>Work item</th><th>Stage</th><th>Accountable owner</th><th>Target</th><th>Status</th><th></th></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td><strong>{item.name}</strong><small>{item.id}</small></td><td>{item.stage}</td><td>{item.owner}</td><td>{item.target}</td><td><StatusBadge status={item.status} /></td><td><Link className="row-link" aria-label={`Open ${item.name}`} to={`/work-items/${item.id}`}>→</Link></td></tr>)}</tbody></table></div></section>
}

function WorkItemsPage() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('All')
  const filtered = useMemo(() => workItems.filter((item) => (status === 'All' || item.status === status) && `${item.name} ${item.id} ${item.owner}`.toLowerCase().includes(query.toLowerCase())), [query, status])
  return <><PageHeader eyebrow="Operational queue" title="Work items" description="Find current ownership, stage, next action, and risk status." actions={<><Link className="button secondary" to="/imports/new">Import CSV</Link><Link className="button primary" to="/work-items/new">New work item</Link></>} /><div className="toolbar"><label><span>Search</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, ID, or owner" /></label><label><span>Status</span><select value={status} onChange={(event) => setStatus(event.target.value)}><option>All</option><option>On track</option><option>At risk</option><option>Blocked</option></select></label><p>{filtered.length} results</p></div><WorkTable items={filtered} title="All active work" /></>
}

function WorkItemPage() {
  const { id } = useParams()
  const item = workItems.find((candidate) => candidate.id === id)
  if (!item) return <Navigate to="/work-items" replace />
  return <><PageHeader eyebrow={item.id} title={item.name} description={`Last updated ${item.updated}`} actions={<Link className="button secondary" to="/work-items">Back to work items</Link>} /><section className="detail-grid"><article className="panel detail-card"><h2>Current state</h2><dl><div><dt>Status</dt><dd><StatusBadge status={item.status} /></dd></div><div><dt>Workflow stage</dt><dd>{item.stage}</dd></div><div><dt>Accountable owner</dt><dd>{item.owner}</dd></div><div><dt>Target date</dt><dd>{item.target}</dd></div></dl></article><article className="panel detail-card"><h2>Next required action</h2><p className="next-action">{item.nextAction}</p><p className="muted">This demonstration view does not yet persist changes to the API.</p><button className="button disabled" disabled>Complete action</button></article></section><section className="panel activity"><h2>Recent activity</h2><div><span></span><p><strong>risk_detected</strong><small>Rule-based evaluation marked this item {item.status.toLowerCase()}.</small></p><time>{item.updated}</time></div><div><span></span><p><strong>owner_assigned</strong><small>{item.owner} became the accountable owner.</small></p><time>Yesterday</time></div></section></>
}

function NewWorkItemPage() {
  const [submitted, setSubmitted] = useState(false)
  const navigate = useNavigate()
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setSubmitted(true) }
  if (submitted) return <SuccessPanel title="Work item validated" message="The form works in demonstration mode. API persistence will be connected in the next implementation slice." onDone={() => navigate('/work-items')} />
  return <><PageHeader eyebrow="Manual intake" title="Create a work item" description="Start a synthetic Northstar contract-to-launch workflow." /><form className="panel form-card" onSubmit={submit}><div className="form-grid"><label><span>Work item name</span><input required placeholder="Example: Redwood Realty" /></label><label><span>Target date</span><input required type="date" /></label><label><span>Accountable owner</span><select required defaultValue=""><option value="" disabled>Select an owner</option><option>Maya Chen</option><option>Jordan Lee</option><option>Avery Brooks</option></select></label><label><span>Initial stage</span><select defaultValue="Intake"><option>Intake</option><option>Validation</option></select></label><label className="full"><span>Summary</span><textarea required placeholder="Describe the work and expected outcome" rows={5} /></label></div><div className="form-actions"><Link className="button secondary" to="/work-items">Cancel</Link><button className="button primary" type="submit">Validate work item</button></div></form></>
}

function ImportPage() {
  const [fileName, setFileName] = useState('')
  const [ready, setReady] = useState(false)
  return <><PageHeader eyebrow="Bulk intake" title="Import work items" description="Choose a CSV file and review it before any records are created." />{ready ? <SuccessPanel title="CSV ready for validation" message={`${fileName} was selected successfully. Row-level parsing and API processing are scheduled for the integration phase.`} onDone={() => setReady(false)} /> : <section className="panel upload-card"><div className="upload-icon">CSV</div><h2>Select a workflow file</h2><p>Expected columns: title, target_date, owner_email, and configured template fields.</p><label className="file-input"><span>{fileName || 'Choose CSV file'}</span><input accept=".csv,text/csv" onChange={(event) => setFileName(event.target.files?.[0]?.name ?? '')} type="file" /></label><button className="button primary" disabled={!fileName} onClick={() => setReady(true)}>Preview import</button><Link to="/work-items">Cancel</Link></section>}</>
}

function SuccessPanel({ title, message, onDone }: { title: string; message: string; onDone: () => void }) {
  return <section className="panel success-panel"><span>✓</span><h2>{title}</h2><p>{message}</p><button className="button primary" onClick={onDone}>Continue</button></section>
}

function ApprovalsPage() { return <><PageHeader eyebrow="Decision control" title="Approvals" description="Review structured decisions and identify overdue requests." /><SimpleTable headers={['Work item','Approval','Approver','Requested','Status']} rows={approvals.map((a) => [a.item,a.type,a.approver,a.requested,<StatusBadge status={a.status} />])} /></> }
function ExceptionsPage() { return <><PageHeader eyebrow="Exception management" title="Exceptions" description="See every blocker, its severity, owner, and age." /><SimpleTable headers={['Exception','Work item','Severity','Owner','Age']} rows={exceptions.map((e) => [e.title,e.item,<StatusBadge status={e.severity} />,e.owner,e.age])} /></> }
function AuditPage() { return <><PageHeader eyebrow="Traceability" title="Audit history" description="Review append-only workflow events from users, rules, and integrations." /><SimpleTable headers={['Event','Work item','Actor or source','Time']} rows={auditEvents.map((e) => [e.event,e.item,e.actor,e.time])} /></> }

function SimpleTable({ headers, rows }: { headers: string[]; rows: ReactNode[][] }) { return <section className="panel table-panel"><div className="table-scroll"><table><thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div></section> }

const foundationPages: Record<string, { eyebrow: string; title: string; description: string; cards: { title: string; body: string; status: string }[] }> = {
  integrations: { eyebrow: 'Connected operations', title: 'Integrations', description: 'Monitor inbound events, adapters, and processing outcomes.', cards: [{ title: 'Generic webhook', body: 'Accepts versioned external events with idempotency protection.', status: 'Contract ready' },{ title: 'CSV intake', body: 'Provides accessible bulk intake without a custom connector.', status: 'Interface active' },{ title: 'REST API', body: 'Exposes the health endpoint today. Workflow resources are next.', status: 'Foundation active' }] },
  templates: { eyebrow: 'Workflow administration', title: 'Workflow templates', description: 'Configure reusable stages, fields, approvals, requirements, and rules.', cards: [{ title: 'Northstar contract-to-launch', body: 'The bundled synthetic scenario used throughout FlowLens.', status: 'Design complete' },{ title: 'Template versioning', body: 'Published versions remain immutable for historical accuracy.', status: 'Implementation queued' }] },
  people: { eyebrow: 'Access and ownership', title: 'People and roles', description: 'Define who can administer, contribute, approve, audit, and view.', cards: [{ title: 'Platform administrator', body: 'Manages application and organization settings.', status: 'Role defined' },{ title: 'Workflow contributor', body: 'Completes assigned operational work.', status: 'Role defined' },{ title: 'Approver', body: 'Records structured business decisions.', status: 'Role defined' }] },
  settings: { eyebrow: 'Platform administration', title: 'Settings', description: 'Configure organization defaults and demonstration behavior.', cards: [{ title: 'Organization', body: 'Northstar Business Services', status: 'Synthetic' },{ title: 'Environment', body: 'Demonstration mode prevents real production data use.', status: 'Active' },{ title: 'Persistence', body: 'PostgreSQL configuration begins in the next foundation milestone.', status: 'Not connected' }] },
}

function FoundationPage({ page }: { page: keyof typeof foundationPages }) { const content = foundationPages[page]; return <><PageHeader eyebrow={content.eyebrow} title={content.title} description={content.description} /><div className="feature-grid">{content.cards.map((card) => <article className="panel feature-card" key={card.title}><StatusBadge status={card.status} /><h2>{card.title}</h2><p>{card.body}</p><small>This capability is shown honestly at its current implementation stage.</small></article>)}</div></> }

function App() {
  return <Layout><Routes><Route path="/" element={<OverviewPage />} /><Route path="/work-items" element={<WorkItemsPage />} /><Route path="/work-items/new" element={<NewWorkItemPage />} /><Route path="/work-items/:id" element={<WorkItemPage />} /><Route path="/imports/new" element={<ImportPage />} /><Route path="/approvals" element={<ApprovalsPage />} /><Route path="/exceptions" element={<ExceptionsPage />} /><Route path="/integrations" element={<FoundationPage page="integrations" />} /><Route path="/audit" element={<AuditPage />} /><Route path="/templates" element={<FoundationPage page="templates" />} /><Route path="/people" element={<FoundationPage page="people" />} /><Route path="/settings" element={<FoundationPage page="settings" />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></Layout>
}

export default App
