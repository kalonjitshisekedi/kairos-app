# Matching and requests specification

**Document version:** 1.0  
**Last updated:** 17 December 2025  
**Status:** Ready for implementation

This specification defines how expert matching works and how clients, experts, and admins interact once a consultation request exists.

---

## 1. Expert discovery and matching model

### 1.1 Request categorisation

When a client submits a consultation request, it is categorised by three primary dimensions:

#### Expertise tags

| Field | Source | Purpose |
|-------|--------|---------|
| `preferred_expertise` | ManyToMany to `ExpertiseTag` | Tags selected by client during submission |
| Tag types | `discipline`, `sector`, `skill` | Classification of expertise areas |

The system matches tags between client requests and expert profiles via the `expertise_tags` field on `ExpertProfile`.

#### Sector alignment

| Field | Location | Purpose |
|-------|----------|---------|
| `sector_expertise` | ExpertProfile | Free-text description of industry sectors |
| `company` | ClientRequest | Client's organisation for sector inference |
| Problem description keywords | ClientRequest | Admin analyses for sector relevance |

Sector matching is manual—admin reviews the client's company and problem description to identify relevant industry context.

#### Engagement type

| Type | Database value | Typical matching criteria |
|------|----------------|---------------------------|
| Consultation | `consultation` | Experts with availability for calls/meetings |
| Research | `research` | Experts with research background, project capacity |
| Advisory | `advisory` | Senior experts with strategic experience |

### 1.2 Admin matching workflow

```
Step 1: New request arrives (status: pending)
    |
Step 2: Admin reviews request details
    |
Step 3: Admin searches expert pool by:
    - Expertise tags
    - Sector experience
    - Availability
    - Years of experience
    - Privacy level (can include private experts)
    |
Step 4: Admin creates shortlist (1-5 experts)
    |
Step 5: Admin sets internal_priority score
    |
Step 6: Admin updates status to 'in_review'
    |
Step 7: Admin contacts selected expert(s)
    |
Step 8: Expert confirms availability
    |
Step 9: Admin updates matched_expert field
    |
Step 10: Status changes to 'matched'
    |
Step 11: Admin sends proposal to client
    |
Step 12: Status changes to 'proposal_sent'
```

### 1.3 Shortlist presentation to client

The shortlist is presented to verified clients only. Content varies by privacy tier:

#### Public experts (`privacy_level='public'`)

Client sees:
- Full name
- Avatar/photo
- Headline
- Bio (first 300 characters)
- Expertise tags
- Years of experience
- Affiliation/organisation
- Average rating and review count
- Availability indicator

#### Semi-private experts (`privacy_level='semi_private'`)

Client sees (verified clients only):
- Full name
- Avatar/photo
- Headline
- Bio (first 300 characters)
- Expertise tags
- Years of experience
- Affiliation/organisation
- Average rating and review count
- Availability indicator

#### Private experts (`privacy_level='private'`)

Client sees (after admin match only):
- First name and last initial (e.g., "John S.")
- Headline
- Expertise tags
- Years of experience
- Affiliation (organisation name only)

**Never revealed for private experts:**
- Full name (until booking confirmed)
- Avatar/photo
- Full bio
- Direct contact information

### 1.4 Data visibility rules by privacy tier

| Data field | Public | Semi-private | Private (matched) |
|------------|--------|--------------|-------------------|
| Full name | Yes | Yes | No (first name + initial) |
| Avatar | Yes | Yes | No |
| Headline | Yes | Yes | Yes |
| Bio (full) | Yes | Yes | No |
| Expertise tags | Yes | Yes | Yes |
| Years experience | Yes | Yes | Yes |
| Affiliation | Yes | Yes | Organisation only |
| Location | Yes | Yes | No |
| Languages | Yes | Yes | No |
| Rating/reviews | Yes | Yes | No |
| Email/phone | **Never** | **Never** | **Never** |
| ORCID | Yes | Yes | No |

---

## 2. Connection initiation: two parallel paths

### 2.1 Path A: Direct client-to-expert via platform messaging

#### Trigger conditions

A verified client can initiate direct messaging when:
1. Client has `email_verified=True`
2. A booking exists between client and expert
3. Booking status is `requested`, `accepted`, `scheduled`, `in_session`, or `completed`

**Critical rule:** Messaging is only available within an active or completed booking context. There is no general inquiry messaging outside of bookings.

#### Required permissions

| User type | Can initiate message | Conditions |
|-----------|---------------------|------------|
| Unverified client | No | Must verify email first |
| Verified client | Yes | Booking must exist |
| Expert | Yes | Booking must exist |
| Admin | Yes | Full access to all threads |

#### What is revealed in messaging

| Data | Revealed | Notes |
|------|----------|-------|
| Display name | Yes | Full name of sender |
| Message content | Yes | Full text visible |
| Message timestamp | Yes | Date and time shown |
| Read status | Yes | Shows if message was read |
| Email address | **No** | Never shown in UI |
| Phone number | **No** | Never shown in UI |
| External contact details | **No** | Blocked in message content |

**Content filtering (recommended):**
- Scan outgoing messages for email patterns (regex: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`)
- Scan for phone patterns (regex: `\+?[0-9\s\-\(\)]{10,}`)
- Flag or redact detected contact information
- Log attempts for admin review

#### Notification rules

| Event | Notification method | Recipient | Timing |
|-------|---------------------|-----------|--------|
| New message received | Email | Other party | Immediate |
| Message read | None | N/A | No notification |
| Multiple unread messages | Email digest | Recipient | Daily (optional) |

Email notification content:
```
Subject: New message - Kairos
Body: You have a new message from {sender_name}:

{message_preview (first 200 chars)}...

Log in to reply.
```

### 2.2 Path B: Admin-facilitated meeting setup

#### Trigger conditions

Admin-facilitated setup occurs when:
1. Client explicitly requests facilitation (checkbox or message)
2. Expert is private (admin must introduce)
3. Complex engagement requiring admin involvement
4. High-value or sensitive engagement

#### Admin workflow steps

```
Step 1: Client request received
    |
Step 2: Admin identifies suitable expert(s)
    |
Step 3: Admin contacts expert via internal channel
    - Email to expert with sanitised brief
    - No client contact details shared yet
    |
Step 4: Expert confirms interest/availability
    |
Step 5: Admin creates booking record (status: draft)
    |
Step 6: Admin sets engagement terms:
    - Proposed price (amount)
    - Expert payout rate
    - Scope description
    - Duration estimate
    |
Step 7: Admin sends proposal to client
    - Status: proposal_sent
    |
Step 8: Client reviews and accepts
    |
Step 9: Admin confirms booking
    - Status: confirmed
    - MessageThread created
    |
Step 10: Parties can now message directly
```

#### What the expert receives

**Initial outreach (before acceptance):**
- Company name (client)
- Anonymised problem description
- Engagement type
- Timeline/urgency
- Budget range (if specified)
- Required expertise areas

**Not shared initially:**
- Client name
- Client email
- Client phone
- Detailed brief document

**After acceptance:**
- Client first name
- Full problem description
- Brief document access
- Messaging access

#### Scheduling and confirmation steps

| Step | Actor | Action | Result |
|------|-------|--------|--------|
| 1 | Admin | Creates booking with proposed times | Booking status: draft |
| 2 | Expert | Reviews and proposes availability | Slots suggested |
| 3 | Admin | Coordinates with client | Time agreed |
| 4 | Admin | Sets `scheduled_start` and `scheduled_end` | Booking status: scheduled |
| 5 | System | Sends calendar invites | Both parties notified |
| 6 | System | Creates Jitsi room ID | `jitsi_room_id` populated |

---

## 3. Expert request management

### 3.1 Where experts see incoming requests

Experts view incoming requests in their dashboard at `/experts/dashboard/`:

| View | Content | Status filter |
|------|---------|---------------|
| Pending requests | Bookings awaiting response | `status='requested'` |
| Active engagements | Confirmed or in-progress | `status__in=['accepted', 'scheduled', 'in_session']` |
| Past engagements | Completed or cancelled | `status__in=['completed', 'archived', 'cancelled']` |

Dashboard displays for each request:
- Client name (first name if private match)
- Problem statement (first 150 characters)
- Service type
- Scheduled time (if set)
- Time since request submitted
- Accept/Decline buttons

### 3.2 Accept/decline interface behaviour

#### Accept action

| Step | System behaviour |
|------|------------------|
| 1 | Expert clicks "Accept" button |
| 2 | Confirmation modal appears |
| 3 | Expert confirms acceptance |
| 4 | Booking status → `accepted` |
| 5 | `responded_at` timestamp set |
| 6 | Client receives email notification |
| 7 | MessageThread becomes active |
| 8 | Expert redirected to booking detail |

Notification to client:
```
Subject: Expert confirmed - Kairos
Body: Good news! {expert_name} has accepted your consultation request.

{problem_statement preview}

Log in to view details and start messaging.
```

#### Decline action

| Step | System behaviour |
|------|------------------|
| 1 | Expert clicks "Decline" button |
| 2 | Decline reason modal appears |
| 3 | Expert selects reason (dropdown) + optional notes |
| 4 | System records decline |
| 5 | Request returns to admin queue |
| 6 | Admin notified of decline |
| 7 | Client not notified of decline (admin handles) |

Decline reason options:
- Not available during requested timeframe
- Outside my area of expertise
- Conflict of interest
- Capacity constraints
- Other (free text required)

### 3.3 Response timeouts

| Urgency level | Expert response deadline | Escalation action |
|---------------|-------------------------|-------------------|
| Critical | 4 hours | Auto-escalate to admin |
| High | 12 hours | Auto-escalate to admin |
| Medium | 24 hours | Auto-escalate to admin |
| Low | 48 hours | Auto-escalate to admin |

#### Timeout handling workflow

```
Request created (status: requested)
    |
    ├── Expert responds within deadline
    |       └── Normal flow continues
    |
    └── Deadline passes without response
            |
            Step 1: System flags request as "awaiting response"
            |
            Step 2: Admin receives escalation notification
            |
            Step 3: Admin options:
                a) Extend deadline (send reminder to expert)
                b) Reassign to different expert
                c) Contact expert directly
            |
            Step 4: If no response after extension:
                - Request returned to matching queue
                - Original expert flagged for follow-up
```

### 3.4 Decline handling rules

#### Automatic return to admin

When an expert declines:
1. Booking status remains `requested` but `matched_expert` cleared
2. `ClientRequest.status` reverts to `in_review`
3. Admin receives notification with decline reason
4. Request appears in admin "needs attention" queue

#### Reassignment to another expert

| Step | Actor | Action |
|------|-------|--------|
| 1 | Admin | Reviews decline reason |
| 2 | Admin | Searches for alternative expert |
| 3 | Admin | Updates `matched_expert` to new expert |
| 4 | Admin | Status → `matched` |
| 5 | System | Notifies new expert |
| 6 | Process | Restarts from accept/decline |

#### Client notification wording

Clients are not directly notified of expert declines. Instead:

**If reassignment is quick (within 24 hours):**
- No notification sent
- Client sees "Matching in progress" status

**If delay exceeds 24 hours:**
```
Subject: Update on your request - Kairos
Body: We are still working on finding the best expert match for your request.

Your request: {problem_statement preview}

Our team is reviewing candidates to ensure the best fit. We will update you within {timeframe} hours.

If you have questions, please reply to this email.
```

**When new expert is matched:**
```
Subject: Expert matched - Kairos
Body: We have identified an expert for your consultation request.

Your request: {problem_statement preview}

Expert: {expert_name}
Expertise: {expertise_tags}

Log in to view the proposal and confirm.
```

---

## 4. Edge cases

### 4.1 Client changes scope mid-request

#### Before expert matched

| Condition | Handling |
|-----------|----------|
| Status: pending or in_review | Client can edit request directly |
| System | Records edit timestamp in `updated_at` |
| Admin | Sees "edited" flag in queue |
| Matching | May need to restart if scope changed significantly |

#### After expert matched

| Condition | Handling |
|-----------|----------|
| Status: matched or proposal_sent | Client contacts admin |
| Admin | Assesses scope change impact |
| Minor change | Admin updates notes, informs expert |
| Major change | Admin may need to rematch |
| Expert | Has right to decline if scope changed materially |

#### After booking confirmed

| Condition | Handling |
|-----------|----------|
| Status: confirmed or scheduled | Requires formal change request |
| Process | Client messages via platform |
| Expert | Must agree to scope change |
| Admin | May adjust pricing if scope increased |
| Documentation | Scope change logged in booking notes |

### 4.2 Expert requests clarification

#### Pre-acceptance clarification

If expert needs clarification before accepting:

1. Expert contacts admin (not client directly)
2. Admin relays question to client
3. Client responds via platform or email
4. Admin shares answer with expert
5. Expert then accepts or declines

**Rationale:** Before acceptance, client/expert communication is gated to:
- Protect expert identity (if private)
- Allow admin to filter inappropriate questions
- Maintain pricing control

#### Post-acceptance clarification

Once booking is confirmed:
1. Expert messages client directly via platform
2. Client receives email notification
3. Conversation continues in-platform
4. Admin can view thread if needed

### 4.3 Multiple experts needed

Some engagements require multiple experts:

#### Panel consultation

| Aspect | Handling |
|--------|----------|
| Structure | Single booking, multiple experts |
| Model | Future: `Booking.experts` ManyToMany field |
| Current workaround | Create separate bookings, link via admin notes |
| Pricing | Aggregate pricing set by admin |
| Scheduling | Admin coordinates joint availability |

#### Sequential consultations

| Aspect | Handling |
|--------|----------|
| Structure | Multiple separate bookings |
| Linking | All reference same `ClientRequest` |
| Pricing | Individual pricing per booking |
| Scheduling | Can be staggered over time |

#### Implementation note

Current model supports single `matched_expert` per booking. For multi-expert scenarios, create one `ClientRequest` with multiple linked `Booking` records.

### 4.4 Client abandons after approval

#### Detection triggers

| Scenario | Detection method |
|----------|------------------|
| No login for 7 days after proposal | Automated check |
| No response to messages for 5 days | Message timestamp check |
| No payment for 14 days after invoice | Payment system integration |

#### Handling workflow

```
Step 1: System flags request as "awaiting client action"
    |
Step 2: Day 3 - Automated reminder email
    |
Step 3: Day 7 - Second reminder email
    |
Step 4: Day 10 - Admin personal outreach
    |
Step 5: Day 14 - Final notice
    |
Step 6: Day 21 - Request marked 'expired'
    - Status → expired
    - Expert released from commitment
    - Booking cancelled if created
```

#### Client notification sequence

**Day 3 reminder:**
```
Subject: Action needed on your consultation request - Kairos
Body: Your expert consultation is ready for confirmation.

Expert: {expert_name}
Request: {problem_statement preview}

Please log in to review and confirm your booking.

[Confirm booking button]
```

**Day 7 reminder:**
```
Subject: Reminder: Consultation awaiting your confirmation - Kairos
Body: We noticed you haven't confirmed your consultation booking yet.

Your matched expert is holding availability for you. Please confirm soon to secure your slot.

[Confirm booking button]

If you need to discuss changes, please reply to this email.
```

**Day 14 final notice:**
```
Subject: Final notice: Consultation request expiring - Kairos
Body: Your consultation request will expire in 7 days if not confirmed.

After expiration, you will need to submit a new request.

[Confirm booking button]

If you need assistance, please contact us.
```

---

## 5. State machine diagram

### 5.1 Client request lifecycle

```
                                    ┌─────────────────┐
                                    │    SUBMITTED    │
                                    │    (pending)    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                               ┌────│   IN REVIEW     │────┐
                               │    │   (in_review)   │    │
                               │    └────────┬────────┘    │
                               │             │             │
                               │             ▼             │
                               │    ┌─────────────────┐    │
                               │    │    MATCHED      │    │
                               │    │    (matched)    │◄───┤
                               │    └────────┬────────┘    │
                               │             │             │
                               │             ▼             │
                               │    ┌─────────────────┐    │
                               │    │ PROPOSAL SENT   │    │
                               │    │ (proposal_sent) │    │
                               │    └────────┬────────┘    │
                               │             │             │
                        ┌──────┴─────────────┼─────────────┴──────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
               ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
               │   CANCELLED     │  │   CONFIRMED     │  │    EXPIRED      │
               │   (cancelled)   │  │   (confirmed)   │  │    (expired)    │
               └─────────────────┘  └────────┬────────┘  └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  IN PROGRESS    │
                                    │  (in_progress)  │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   COMPLETED     │
                                    │   (completed)   │
                                    └─────────────────┘
```

### 5.2 Booking lifecycle

```
                                    ┌─────────────────┐
                                    │     DRAFT       │
                                    │    (draft)      │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                               ┌────│   REQUESTED     │────┐
                               │    │   (requested)   │    │
                               │    └────────┬────────┘    │
                               │             │             │
                               │      Expert │             │
                               │    responds │             │ Expert
                               │             │             │ declines
                               │             ▼             │
                               │    ┌─────────────────┐    │
                               │    │    ACCEPTED     │    │
                               │    │   (accepted)    │    │
                               │    └────────┬────────┘    │
                               │             │             │
                               │             ▼             │
                               │    ┌─────────────────┐    │
                               │    │   SCHEDULED     │    │
                               │    │   (scheduled)   │    │
                               │    └────────┬────────┘    │
                               │             │             │
                        ┌──────┴─────────────┼─────────────┴──────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
               ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
               │   CANCELLED     │  │   IN SESSION    │  │ Returns to      │
               │   (cancelled)   │  │  (in_session)   │  │ admin queue     │
               └─────────────────┘  └────────┬────────┘  └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   COMPLETED     │
                                    │   (completed)   │
                                    └────────┬────────┘
                                             │
                               ┌─────────────┴─────────────┐
                               │                           │
                               ▼                           ▼
                      ┌─────────────────┐         ┌─────────────────┐
                      │    ARCHIVED     │         │    DISPUTED     │
                      │   (archived)    │         │   (disputed)    │
                      └─────────────────┘         └─────────────────┘
```

### 5.3 Complete flow: request to scheduled booking

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  CLIENT                    ADMIN                        EXPERT              │
│                                                                             │
│  ┌──────────────┐                                                           │
│  │ Submit       │                                                           │
│  │ request      │─────────────────┐                                         │
│  └──────────────┘                 │                                         │
│                                   ▼                                         │
│                          ┌──────────────┐                                   │
│                          │ Review       │                                   │
│                          │ request      │                                   │
│                          └──────┬───────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│                          ┌──────────────┐                                   │
│                          │ Search       │                                   │
│                          │ experts      │                                   │
│                          └──────┬───────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│                          ┌──────────────┐        ┌──────────────┐           │
│                          │ Create       │───────▶│ Review       │           │
│                          │ shortlist    │        │ opportunity  │           │
│                          └──────────────┘        └──────┬───────┘           │
│                                                         │                   │
│                                                         ▼                   │
│                                                  ┌──────────────┐           │
│                                                  │ Accept or    │           │
│                                                  │ decline      │           │
│                                                  └──────┬───────┘           │
│                                                         │                   │
│                                 ┌───────────────────────┘                   │
│                                 │                                           │
│                                 ▼                                           │
│                          ┌──────────────┐                                   │
│                          │ Update match │                                   │
│                          │ status       │                                   │
│                          └──────┬───────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────┐        ┌──────────────┐                                   │
│  │ Receive      │◀───────│ Send         │                                   │
│  │ proposal     │        │ proposal     │                                   │
│  └──────┬───────┘        └──────────────┘                                   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────┐                                                           │
│  │ Accept       │                                                           │
│  │ proposal     │─────────────────┐                                         │
│  └──────────────┘                 │                                         │
│                                   ▼                                         │
│                          ┌──────────────┐                                   │
│                          │ Create       │                                   │
│                          │ booking      │                                   │
│                          └──────┬───────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐           │
│  │ Messaging    │◀──────▶│ Coordinate   │◀──────▶│ Messaging    │           │
│  │ enabled      │        │ scheduling   │        │ enabled      │           │
│  └──────────────┘        └──────┬───────┘        └──────────────┘           │
│                                 │                                           │
│                                 ▼                                           │
│                          ┌──────────────┐                                   │
│                          │ SCHEDULED    │                                   │
│                          │ ✓ Complete   │                                   │
│                          └──────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Status transition rules

| From status | To status | Trigger | Actor |
|-------------|-----------|---------|-------|
| pending | in_review | Admin opens request | Admin |
| pending | cancelled | Client cancels | Client/Admin |
| in_review | matched | Expert identified | Admin |
| in_review | cancelled | No suitable expert | Admin |
| matched | proposal_sent | Proposal emailed | Admin |
| matched | in_review | Expert declines | System |
| proposal_sent | confirmed | Client accepts | Client |
| proposal_sent | expired | No response (21 days) | System |
| proposal_sent | cancelled | Client declines | Client |
| confirmed | in_progress | Work begins | Admin/System |
| in_progress | completed | Work finished | Admin |

---

## 6. Implementation checklist

### 6.1 Matching system

- [ ] Implement shortlist model (or use admin notes field)
- [ ] Add expert search filters for admin (tags, sector, availability)
- [ ] Create admin interface for matching workflow
- [ ] Add `internal_priority` scoring logic
- [ ] Implement privacy-aware expert display in proposals

### 6.2 Connection paths

- [ ] Ensure messaging gated to verified clients only
- [ ] Implement message content filtering for contact details
- [ ] Add email notification on new message
- [ ] Create admin-facilitated booking flow
- [ ] Implement proposal email template

### 6.3 Expert request management

- [ ] Build expert dashboard with request queue
- [ ] Implement accept/decline interface with reason capture
- [ ] Add response timeout monitoring
- [ ] Create escalation notification for admin
- [ ] Implement decline-and-reassign workflow

### 6.4 Edge case handling

- [ ] Add scope change request flow
- [ ] Implement pre-acceptance clarification via admin
- [ ] Support multi-booking for single request
- [ ] Build abandonment detection and reminder sequence
- [ ] Create expiration automation

### 6.5 State management

- [ ] Validate all status transitions
- [ ] Add audit logging for status changes
- [ ] Implement status rollback for admin (if needed)
- [ ] Create status change email notifications

---

*End of specification*
