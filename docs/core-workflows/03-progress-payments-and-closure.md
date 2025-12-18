# Progress, payments, and closure specification

**Document version:** 1.0  
**Last updated:** 18 December 2025  
**Implementation Status:** Partially implemented

## Implementation Status

### Implemented Features
- ✅ Invoice-based payment model (no card checkout at platform level)
- ✅ Invoice status workflow (draft → sent → paid)
- ✅ Invoice creation and sending to clients
- ✅ Booking status lifecycle (draft → requested → accepted → scheduled → in_session → completed)
- ✅ Expert payout eligibility tracking
- ✅ Completion marking by expert
- ✅ Client satisfaction confirmation flow
- ✅ Audit logging for all actions

### Planned Next
- Auto-confirmation after 7 days without client response
- Dispute handling workflow with resolution options
- Record archiving and anonymization (POPIA compliance)
- Real-time progress bar updates (currently manual refresh)
- Rework request handling for minor revisions
- Payment confirmation automation via bank API

This specification defines operational workflows for communication, invoice-based payments, progress tracking, and engagement completion across all user types.

---

## 1. Communication rules

### 1.1 Platform messaging principle

**Core rule:** All client-expert communication happens inside the platform.

| Channel | Status | Rationale |
|---------|--------|-----------|
| Platform messaging | Primary | Auditable, secure, consistent |
| Email notifications | Secondary | Alerts only, no content exchange |
| Phone/SMS | Prohibited | Cannot be audited |
| External messaging | Prohibited | Data leakage risk |

### 1.2 Contact information protection

#### Never exposed

| Data type | Protection level | Enforcement |
|-----------|------------------|-------------|
| Email addresses | Never shown in UI | Server-side filtering |
| Phone numbers | Never shown in UI | Server-side filtering |
| Personal addresses | Never collected | Not in data model |
| Social media handles | Expert controls | Privacy settings |

#### Content filtering implementation

Outgoing messages must be scanned for contact information:

```
Email pattern: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
Phone pattern: \+?[0-9\s\-\(\)]{10,}
```

| Scenario | Action |
|----------|--------|
| Pattern detected | Flag message for review |
| Repeat offender | Admin notification |
| Confirmed violation | Warning to user, message blocked |

**Exception:** Admin-facilitated introductions may share contact details when explicitly authorised by both parties.

### 1.3 File sharing rules

#### Allowed file types

| Category | Extensions | Max size |
|----------|------------|----------|
| Documents | .pdf, .doc, .docx | 10 MB |
| Spreadsheets | .xls, .xlsx, .csv | 10 MB |
| Presentations | .ppt, .pptx | 20 MB |
| Images | .jpg, .jpeg, .png, .gif | 5 MB |
| Archives | .zip | 25 MB |

#### Prohibited file types

| Category | Extensions | Reason |
|----------|------------|--------|
| Executables | .exe, .bat, .sh, .app | Security risk |
| Scripts | .js, .py, .php | Security risk |
| Disk images | .iso, .dmg | Size and security |

#### File sharing contexts

| Context | Who can upload | Visibility |
|---------|----------------|------------|
| Message attachment | Client, Expert | Both parties + Admin |
| Booking attachment | Client, Expert | Both parties + Admin |
| Brief document | Client | Admin + Matched expert |
| Deliverable | Expert | Client + Admin |

### 1.4 Audit logging requirements

#### Events requiring audit logs

| Event | Log type | Data captured |
|-------|----------|---------------|
| Message sent | `MESSAGE_SENT` | Sender, thread, timestamp, content hash |
| Message read | `MESSAGE_READ` | Reader, message ID, timestamp |
| File uploaded | `FILE_UPLOADED` | Uploader, filename, size, context |
| File downloaded | `FILE_DOWNLOADED` | Downloader, file ID, timestamp |
| Contact info detected | `CONTENT_FLAGGED` | User, message ID, pattern type |

#### Audit log model fields

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Unique identifier |
| `user` | ForeignKey | Acting user |
| `event_type` | CharField | Event classification |
| `description` | TextField | Human-readable summary |
| `ip_address` | GenericIPAddressField | Request origin |
| `user_agent` | TextField | Browser/client info |
| `metadata` | JSONField | Event-specific data |
| `created_at` | DateTimeField | Timestamp |

#### Retention policy

| Log type | Retention period | Archive method |
|----------|------------------|----------------|
| Security events | 7 years | Cold storage |
| Transaction logs | 5 years | Cold storage |
| Communication logs | 3 years | Compressed archive |
| Session logs | 1 year | Deletion after period |

---

## 2. Payment model (invoice-based)

### 2.1 Pricing philosophy

**Core principle:** Pricing is determined during the proposal stage, not during checkout.

| Stage | Pricing action | Actor |
|-------|----------------|-------|
| Request submission | Client provides budget range (optional) | Client |
| Admin review | Admin assesses scope and complexity | Admin |
| Expert matching | Admin considers expert rates | Admin |
| Proposal creation | Admin sets `proposed_price` | Admin |
| Client confirmation | Client accepts quoted price | Client |

### 2.2 Invoice workflow

#### Invoice statuses

| Status | Database value | Meaning |
|--------|----------------|---------|
| Draft | `draft` | Invoice created, not yet sent |
| Sent | `sent` | Invoice emailed to client |
| Paid | `paid` | Payment received and confirmed |
| Cancelled | `cancelled` | Invoice voided |

#### Workflow diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INVOICE LIFECYCLE                                  │
│                                                                             │
│  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐           │
│  │    DRAFT     │───────▶│     SENT     │───────▶│     PAID     │           │
│  │              │        │              │        │              │           │
│  └──────┬───────┘        └──────┬───────┘        └──────────────┘           │
│         │                       │                                           │
│         │                       │                                           │
│         ▼                       ▼                                           │
│  ┌──────────────┐        ┌──────────────┐                                   │
│  │  CANCELLED   │        │  CANCELLED   │                                   │
│  │  (voided)    │        │  (disputed)  │                                   │
│  └──────────────┘        └──────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Invoice creation trigger

| Trigger | Actor | Conditions |
|---------|-------|------------|
| Manual creation | Admin | After client confirms proposal |
| System creation | Automated | After Stripe payment (if card flow used) |

**Primary flow (invoice-based):**

```
Step 1: Client confirms proposal (status: confirmed)
    |
Step 2: Admin creates invoice in draft
    - Sets amount from proposed_price
    - Sets description from engagement scope
    - Links to booking
    |
Step 3: Admin reviews billing details
    - Confirms billing_email
    - Adds organisation_name if provided
    - Adds po_number if provided
    |
Step 4: Admin sends invoice
    - invoice_status → sent
    - Email sent to billing_email
    |
Step 5: Client receives invoice
    - Payment terms displayed (e.g., 14 days)
    |
Step 6: Client processes payment
    - Bank transfer or EFT
    - References invoice number
    |
Step 7: Admin confirms payment
    - invoice_status → paid
    - Records payment date
    |
Step 8: Engagement may proceed
```

### 2.3 Billing information collection

#### What client provides

| Field | Required | When collected | Validation |
|-------|----------|----------------|------------|
| `billing_email` | Yes | Proposal confirmation | Valid email format |
| `organisation_name` | No | Proposal confirmation | Max 200 characters |
| `po_number` | No | Proposal confirmation | Max 100 characters |

#### Billing collection interface

When client confirms a proposal, display:

```
Billing details
---------------
Billing email: [________________] (required)
Organisation name: [________________] (for invoice)
Purchase order number: [________________] (optional)

[ ] I confirm these billing details are correct
```

### 2.4 Payment trigger point

**Policy decision:** Engagement starts after invoice is SENT.

| Payment policy option | Engagement start | Risk profile |
|-----------------------|------------------|--------------|
| Invoice sent | Immediately after sending | Higher risk for admin |
| Invoice paid | Only after payment confirmed | Lower risk, slower start |

**Recommended policy:** Invoice sent

Rationale:
- Enterprise clients often have 30-day payment terms
- Urgency of client needs varies
- Admin can assess client creditworthiness
- Blocking on payment delays time-sensitive engagements

#### Safeguards for invoice-sent policy

| Risk | Mitigation |
|------|------------|
| Non-payment | Credit check for large engagements |
| Scope creep | Clear scope documentation before start |
| Dispute | Signed engagement terms before start |

#### Status transition on invoice sent

```
When invoice_status changes from 'draft' to 'sent':
    IF booking.status == 'confirmed':
        booking.status → 'scheduled' OR 'in_progress'
        Expert notified: "Engagement approved, you may begin"
        Client notified: "Your engagement is confirmed"
```

### 2.5 Expert payout trigger

Expert payout occurs after TWO conditions are met:

1. **Engagement completed** - Booking status = `completed`
2. **Satisfaction confirmed** - Client confirms completion OR 7-day auto-confirmation

#### Payout workflow

```
Step 1: Engagement work delivered
    |
Step 2: Expert marks engagement complete
    - completed_by_expert = True
    |
Step 3: Client receives completion notification
    |
Step 4: Client confirms satisfaction
    - completed_by_client = True
    - OR 7 days elapse without dispute
    |
Step 5: Booking status → completed
    |
Step 6: Payout becomes eligible
    - ExpertPayout created (status: pending)
    |
Step 7: Admin reviews and initiates payout
    - ExpertPayout status → processing
    |
Step 8: Payment transferred to expert
    - ExpertPayout status → completed
    - processed_at timestamp set
```

#### Payout calculation

| Field | Source | Notes |
|-------|--------|-------|
| `amount` | `booking.expert_payout` | Set by admin in proposal |
| Platform fee | `booking.amount - booking.expert_payout` | Retained by platform |
| Currency | `booking.currency` | ZAR default |

---

## 3. Progress tracking

### 3.1 Unified progress model

A single progress indicator tracks engagement status across all views.

#### Progress stages

| Stage | Display label | Description |
|-------|---------------|-------------|
| 1 | Submitted | Request received |
| 2 | Client verified | Email verification complete |
| 3 | Matching in progress | Admin reviewing experts |
| 4 | Expert proposed | Shortlist created |
| 5 | Expert confirmed | Expert accepted engagement |
| 6 | Awaiting payment | Invoice sent |
| 7 | Scheduled | Payment confirmed, session scheduled |
| 8 | In progress | Active engagement |
| 9 | Awaiting confirmation | Expert marked complete |
| 10 | Completed | Client confirmed |
| 11 | Archived | Records archived |

#### Stage mapping to database fields

| Stage | ClientRequest.status | Booking.status | invoice_status | Other conditions |
|-------|---------------------|----------------|----------------|------------------|
| Submitted | pending | - | - | Request created |
| Client verified | pending/in_review | - | - | client.email_verified = True |
| Matching in progress | in_review | - | - | Admin reviewing |
| Expert proposed | matched | draft | - | matched_expert set |
| Expert confirmed | proposal_sent | requested/accepted | - | Expert accepted |
| Awaiting payment | confirmed | accepted | draft/sent | Invoice created |
| Scheduled | confirmed | scheduled | sent/paid | Session time set |
| In progress | in_progress | in_session | paid | Session started |
| Awaiting confirmation | in_progress | completed | paid | completed_by_expert = True |
| Completed | completed | completed | paid | completed_by_client = True |
| Archived | completed | archived | paid | Archive date passed |

### 3.2 Progress bar appearance

#### Visual design

```
[=======○○○○] 55% - Expert confirmed

Stage 1-5: Complete (filled circles/segments)
Stage 6: Current (highlighted, animated)
Stage 7-11: Pending (empty circles/segments)
```

#### Display by user type

| User type | Location | Visible stages |
|-----------|----------|----------------|
| Client | Client dashboard | All stages (1-11) |
| Client | Request detail page | All stages with detail |
| Expert | Expert dashboard | Stages 5-11 only |
| Expert | Engagement detail | Stages 5-11 with detail |
| Admin | Admin dashboard | All stages + internal notes |
| Admin | Request detail | Full timeline with timestamps |

### 3.3 Update triggers

#### What updates the progress bar

| Trigger event | Stage change | Actor |
|---------------|--------------|-------|
| Request submitted | → Submitted | System (on form submit) |
| Email verified | → Client verified | System (on link click) |
| Admin opens request | → Matching in progress | Admin |
| Expert matched | → Expert proposed | Admin |
| Expert accepts | → Expert confirmed | Expert |
| Invoice created | → Awaiting payment | Admin |
| Invoice sent | → Awaiting payment | Admin |
| Payment confirmed | → Scheduled | Admin |
| Session starts | → In progress | System (time-based) |
| Expert marks complete | → Awaiting confirmation | Expert |
| Client confirms | → Completed | Client |
| 30 days after completion | → Archived | System (scheduled task) |

#### Event logging

Every stage transition creates an audit log entry:

```python
AuditLog.objects.create(
    user=acting_user,
    event_type='STAGE_TRANSITION',
    description=f'Progress: {previous_stage} → {new_stage}',
    metadata={
        'request_id': str(request.id),
        'booking_id': str(booking.id) if booking else None,
        'from_stage': previous_stage,
        'to_stage': new_stage,
    }
)
```

### 3.4 Real-time updates

#### Implementation approach

| Method | Use case | Technical notes |
|--------|----------|-----------------|
| Polling | Default approach | Simple, compatible, 30-second interval |
| WebSockets | Optional enhancement | Lower latency, higher complexity |

#### Polling implementation (recommended)

```
Client dashboard:
- Poll /api/progress/{request_id}/ every 30 seconds
- Response includes current stage + last_updated timestamp
- Update UI only if stage changed

Expert dashboard:
- Poll /api/expert/engagements/active/ every 30 seconds
- Returns list with status for each engagement
- Update badge counts and status indicators
```

#### WebSocket implementation (optional future enhancement)

```
Channel: ws://domain/ws/progress/{request_id}/

Events:
- stage_changed: { stage: 6, label: "Awaiting payment", timestamp: "..." }
- message_received: { thread_id: "...", preview: "..." }
- booking_updated: { booking_id: "...", status: "..." }
```

---

## 4. Completion and closure

### 4.1 What constitutes completion

An engagement is considered complete when:

1. **Deliverables provided** (if applicable)
   - Expert uploads final deliverable files
   - OR Expert confirms work delivered in session

2. **Expert marks complete**
   - Expert clicks "Mark as complete" button
   - `completed_by_expert` = True
   - `completed_at` timestamp if not set

3. **Client confirms satisfaction**
   - Client clicks "Confirm completion" button
   - `completed_by_client` = True
   - `completed_at` timestamp set

4. **OR Auto-confirmation**
   - 7 days elapse after expert marks complete
   - No dispute raised by client
   - System sets `completed_by_client` = True

### 4.2 Client satisfaction confirmation flow

#### Interface for client

When expert marks complete, client sees:

```
Engagement completion
---------------------
{Expert name} has marked this engagement as complete.

Deliverables attached:
- [filename1.pdf] (Download)
- [filename2.docx] (Download)

Are you satisfied with the outcome?

[Confirm completion]     [Request revision]     [Raise dispute]

Note: If you don't respond within 7 days, completion will be 
automatically confirmed.
```

#### Confirmation actions

| Action | Result | Next step |
|--------|--------|-----------|
| Confirm completion | Booking → completed | Payout eligible, review prompt |
| Request revision | Message sent to expert | Expert addresses concerns |
| Raise dispute | Booking → disputed | Admin notified |

#### Post-confirmation flow

```
After client confirms:
    |
Step 1: Thank you message displayed
    |
Step 2: Review prompt shown
    "Would you like to leave a review for {expert_name}?"
    [ Leave review ] [ Skip for now ]
    |
Step 3: If review submitted:
    - Review created (public or private)
    - Expert notified of review
    |
Step 4: Payout becomes eligible
    |
Step 5: Dashboard shows "Completed" status
```

### 4.3 Dispute handling and rework requests

#### Dispute workflow

```
Step 1: Client raises dispute
    - booking.status → disputed
    - Reason captured in form
    |
Step 2: Admin notified immediately
    - Email alert to ops team
    - Dispute appears in admin queue
    |
Step 3: Admin reviews dispute
    - Views message history
    - Reviews deliverables
    - Contacts both parties if needed
    |
Step 4: Admin determines resolution
    Option A: Rework required
    Option B: Partial refund
    Option C: Full refund
    Option D: Dispute rejected (client at fault)
    |
Step 5: Resolution implemented
    - Status updated accordingly
    - Parties notified
    |
Step 6: Case closed
    - Audit log entry created
    - Learning documented
```

#### Rework request handling

| Scenario | Process | Expert compensation |
|----------|---------|---------------------|
| Minor clarification | Expert addresses via messaging | No additional fee |
| Scope misunderstanding | Admin mediates, clarifies | Original fee stands |
| Additional work needed | New booking created | Additional fee |
| Expert failed to deliver | Admin determines remedy | Reduced or withheld |

#### Dispute resolution timeframes

| Dispute type | Target resolution | Escalation |
|--------------|-------------------|------------|
| Minor issue | 3 business days | Super admin at day 3 |
| Scope dispute | 5 business days | Super admin at day 5 |
| Quality dispute | 7 business days | External review if needed |
| Payment dispute | 10 business days | Legal review if needed |

### 4.4 Record archiving and retention

#### Archive trigger

Records move to archived status when:

| Condition | Timeframe | Action |
|-----------|-----------|--------|
| Completed engagement | 30 days after completion | Auto-archive |
| Cancelled engagement | 7 days after cancellation | Auto-archive |
| Expired request | Immediate | Auto-archive |

#### Archive process

```
Step 1: System identifies eligible records
    - Completed > 30 days ago
    - No active disputes
    |
Step 2: Status updated
    - booking.status → archived
    - client_request.status → completed (if not already)
    |
Step 3: Records remain accessible
    - Client can view in "Past engagements"
    - Expert can view in "Engagement history"
    - Admin has full access
    |
Step 4: After retention period
    - Personal data anonymised (per POPIA)
    - Transaction records retained
    - Audit logs retained
```

#### Retention periods

| Data type | Retention | Post-retention action |
|-----------|-----------|----------------------|
| Booking records | 7 years | Anonymise personal data |
| Financial records | 7 years | Archive to cold storage |
| Messages | 3 years | Delete after period |
| Attachments | 3 years | Delete after period |
| Audit logs | 7 years | Archive to cold storage |
| Reviews | Indefinite | Anonymise reviewer after 7 years |

#### Data anonymisation rules (POPIA compliance)

| Field | Anonymisation method |
|-------|---------------------|
| Client name | Hash + "Client-XXXXX" |
| Client email | Delete |
| Client phone | Delete |
| Expert name | Retain (public figure) |
| Message content | Delete or anonymise |
| Booking notes | Anonymise references |

---

## 5. Demo workflow checklist

This checklist validates the full engagement lifecycle using demo accounts.

### 5.1 Prerequisites

Ensure demo accounts exist:

| Account | Email | Role | State |
|---------|-------|------|-------|
| Demo client (unverified) | demo.client.unverified@kairos-test.co.za | client | email_verified=False |
| Demo client (verified) | demo.client@kairos-test.co.za | client | email_verified=True |
| Demo expert (active) | demo.expert@kairos-test.co.za | expert | verification_status='active' |
| Demo ops admin | demo.ops@kairos-test.co.za | admin | is_staff=True |

### 5.2 Full lifecycle test

#### Phase 1: Request submission (as demo client verified)

- [ ] 1.1 Log in as demo.client@kairos-test.co.za
- [ ] 1.2 Navigate to "Submit request" page
- [ ] 1.3 Complete request form:
  - Name: "Demo Test Client"
  - Company: "Test Company Ltd"
  - Problem description: "We need expert advice on market entry strategy for South African fintech sector."
  - Engagement type: Consultation
  - Urgency: Medium
  - Consent: Checked
- [ ] 1.4 Submit request
- [ ] 1.5 Verify confirmation message displayed
- [ ] 1.6 Verify request appears in client dashboard
- [ ] 1.7 Verify progress bar shows "Submitted"

#### Phase 2: Admin matching (as demo ops admin)

- [ ] 2.1 Log in as demo.ops@kairos-test.co.za
- [ ] 2.2 Navigate to Django admin → Client requests
- [ ] 2.3 Find the test request
- [ ] 2.4 Update status to "In review"
- [ ] 2.5 Search experts by "fintech" or relevant tags
- [ ] 2.6 Select demo.expert@kairos-test.co.za as matched expert
- [ ] 2.7 Set proposed_price (e.g., R5,000)
- [ ] 2.8 Set expert_payout (e.g., R4,000)
- [ ] 2.9 Update status to "Matched"
- [ ] 2.10 Verify audit log entry created

#### Phase 3: Expert response (as demo expert)

- [ ] 3.1 Log in as demo.expert@kairos-test.co.za
- [ ] 3.2 Navigate to expert dashboard
- [ ] 3.3 Verify incoming request appears
- [ ] 3.4 Click "View details"
- [ ] 3.5 Verify client name and problem description visible
- [ ] 3.6 Click "Accept" button
- [ ] 3.7 Confirm acceptance in modal
- [ ] 3.8 Verify status changed to "Accepted"
- [ ] 3.9 Verify messaging thread created

#### Phase 4: Proposal and billing (as demo ops admin)

- [ ] 4.1 Log in as demo.ops@kairos-test.co.za
- [ ] 4.2 Navigate to the request in admin
- [ ] 4.3 Update status to "Proposal sent"
- [ ] 4.4 Verify email would be sent to client (check logs)
- [ ] 4.5 Create invoice in draft:
  - Amount: R5,000
  - Description: "Fintech market entry consultation"
- [ ] 4.6 Add billing details:
  - billing_email: demo.client@kairos-test.co.za
  - organisation_name: "Test Company Ltd"
- [ ] 4.7 Send invoice (status → sent)
- [ ] 4.8 Verify invoice email would be sent

#### Phase 5: Payment confirmation (as demo ops admin)

- [ ] 5.1 Simulate payment received
- [ ] 5.2 Update invoice status to "Paid"
- [ ] 5.3 Update booking status to "Scheduled"
- [ ] 5.4 Verify client receives confirmation (check logs)

#### Phase 6: Engagement execution

- [ ] 6.1 As client: Verify progress bar shows "Scheduled"
- [ ] 6.2 As expert: Verify engagement appears in active list
- [ ] 6.3 As client: Send test message to expert
- [ ] 6.4 As expert: Verify message received
- [ ] 6.5 As expert: Reply to message
- [ ] 6.6 As client: Verify reply received
- [ ] 6.7 As admin: Update booking status to "In session"

#### Phase 7: Completion (as demo expert)

- [ ] 7.1 Log in as demo.expert@kairos-test.co.za
- [ ] 7.2 Navigate to engagement detail
- [ ] 7.3 Upload test deliverable (optional)
- [ ] 7.4 Click "Mark as complete"
- [ ] 7.5 Confirm completion
- [ ] 7.6 Verify completed_by_expert = True

#### Phase 8: Client confirmation (as demo client)

- [ ] 8.1 Log in as demo.client@kairos-test.co.za
- [ ] 8.2 Navigate to engagement detail
- [ ] 8.3 Verify completion notification displayed
- [ ] 8.4 Click "Confirm completion"
- [ ] 8.5 Verify status changes to "Completed"
- [ ] 8.6 Verify review prompt appears
- [ ] 8.7 Leave a test review (5 stars, "Excellent advice")
- [ ] 8.8 Verify review saved

#### Phase 9: Payout processing (as demo ops admin)

- [ ] 9.1 Log in as demo.ops@kairos-test.co.za
- [ ] 9.2 Navigate to expert payouts
- [ ] 9.3 Verify payout eligible for demo expert
- [ ] 9.4 Create payout record:
  - Amount: R4,000
  - Status: Pending
- [ ] 9.5 Process payout (simulate):
  - Status: Processing → Completed
  - processed_at set
- [ ] 9.6 Verify audit log entry created

#### Phase 10: Archiving verification

- [ ] 10.1 Verify engagement appears in "Past engagements" for client
- [ ] 10.2 Verify engagement appears in "Engagement history" for expert
- [ ] 10.3 Verify all audit logs present for the engagement
- [ ] 10.4 Verify progress bar shows "Completed"

### 5.3 Edge case tests

#### Test: Client disputes completion

- [ ] Create engagement through Phase 6
- [ ] As expert: Mark complete
- [ ] As client: Click "Raise dispute"
- [ ] Enter dispute reason
- [ ] Verify booking.status = "disputed"
- [ ] Verify admin notified
- [ ] As admin: Review and resolve dispute
- [ ] Verify resolution logged

#### Test: Expert decline

- [ ] Create request through Phase 2
- [ ] As expert: Click "Decline"
- [ ] Select reason: "Capacity constraints"
- [ ] Verify request returns to admin queue
- [ ] Verify client NOT notified of decline
- [ ] As admin: Match different expert (or reuse same for test)

#### Test: Auto-confirmation

- [ ] Create engagement through Phase 7 (expert marks complete)
- [ ] Do NOT confirm as client
- [ ] Wait 7 days (or simulate with date override)
- [ ] Verify system auto-confirms
- [ ] Verify completed_by_client = True
- [ ] Verify payout eligible

---

## 6. Implementation checklist

### 6.1 Communication system

- [ ] Implement contact information filtering in messages
- [ ] Add file type validation for attachments
- [ ] Create file size limits per type
- [ ] Build audit logging for all communication events
- [ ] Add notification email templates

### 6.2 Payment system

- [ ] Implement invoice creation flow in admin
- [ ] Add billing details collection form
- [ ] Create invoice status transitions
- [ ] Build invoice email sending functionality
- [ ] Implement payout eligibility checking
- [ ] Create payout processing workflow

### 6.3 Progress tracking

- [ ] Create unified progress calculation function
- [ ] Build progress bar component for dashboards
- [ ] Implement polling endpoint for real-time updates
- [ ] Add stage transition logging
- [ ] Create progress notifications

### 6.4 Completion and closure

- [ ] Implement dual-confirmation (expert + client) flow
- [ ] Build auto-confirmation scheduler (7-day timer)
- [ ] Create dispute handling workflow
- [ ] Add review collection after completion
- [ ] Build archive automation (30-day scheduler)

### 6.5 Demo system

- [ ] Create demo account setup management command
- [ ] Build demo data fixtures
- [ ] Add demo account reset functionality
- [ ] Document demo credentials securely

---

*End of specification*
