# Access and onboarding specification

**Document version:** 1.0  
**Last updated:** 17 December 2025  
**Status:** Ready for implementation

This specification defines platform access rules, user roles, and onboarding gates for the Kairos expert consultation platform. Developers should implement these rules without ambiguity.

---

## 1. User roles and permissions matrix

### 1.1 Role definitions

The platform uses three primary roles defined in `accounts.models.User.Role`:

| Role | Database value | Description |
|------|----------------|-------------|
| Client | `client` | Individuals or organisations seeking expert consultation |
| Expert | `expert` | Verified professionals offering consultation services |
| Admin | `admin` | Platform operations and management staff |

### 1.2 Client states

| State | Criteria | Database fields |
|-------|----------|-----------------|
| Unverified client | `role='client'` AND `email_verified=False` | User record exists, email not confirmed |
| Verified client | `role='client'` AND `email_verified=True` | Email confirmed via verification link |

### 1.3 Expert states

| State | Criteria | Database fields |
|-------|----------|-----------------|
| Applied expert | `role='expert'` AND `verification_status='applied'` | Profile wizard completed, awaiting vetting |
| Vetted expert | `role='expert'` AND `verification_status='vetted'` | Background verified, not yet active |
| Active expert | `role='expert'` AND `verification_status='active'` | Fully operational, can receive bookings |
| Needs changes | `role='expert'` AND `verification_status='needs_changes'` | Profile requires corrections |
| Rejected expert | `role='expert'` AND `verification_status='rejected'` | Application denied |

### 1.4 Admin states

| State | Criteria | Database fields |
|-------|----------|-----------------|
| Ops admin | `role='admin'` AND `is_staff=True` AND `is_superuser=False` | Day-to-day operations access |
| Super admin | `role='admin'` AND `is_staff=True` AND `is_superuser=True` | Full platform control |

### 1.5 Permissions matrix

#### Public pages (no authentication required)

| Page/Action | Unverified client | Verified client | Applied expert | Vetted/Active expert | Ops admin | Super admin |
|-------------|-------------------|-----------------|----------------|----------------------|-----------|-------------|
| Homepage | Yes | Yes | Yes | Yes | Yes | Yes |
| About page | Yes | Yes | Yes | Yes | Yes | Yes |
| Services/capabilities page | Yes | Yes | Yes | Yes | Yes | Yes |
| Contact page | Yes | Yes | Yes | Yes | Yes | Yes |
| Blog (public posts) | Yes | Yes | Yes | Yes | Yes | Yes |
| Join as expert (careers) | Yes | Yes | Yes | Yes | Yes | Yes |
| Sign up | Yes | N/A | N/A | N/A | N/A | N/A |
| Log in | Yes | Yes | Yes | Yes | Yes | Yes |

#### Expert directory access

| Page/Action | Unverified client | Verified client | Applied expert | Vetted/Active expert | Ops admin | Super admin |
|-------------|-------------------|-----------------|----------------|----------------------|-----------|-------------|
| View public experts | Yes | Yes | Yes | Yes | Yes | Yes |
| View semi-private experts | **No** | **Yes** | No | Yes (own profile) | Yes | Yes |
| View private experts | **No** | **No** | No | Yes (own profile only) | Yes | Yes |

#### Authenticated client pages

| Page/Action | Unverified client | Verified client | Applied expert | Vetted/Active expert | Ops admin | Super admin |
|-------------|-------------------|-----------------|----------------|----------------------|-----------|-------------|
| Client dashboard | Yes | Yes | N/A | N/A | Yes | Yes |
| Submit consultation request | Yes | Yes | N/A | N/A | Yes | Yes |
| View own requests | Yes | Yes | N/A | N/A | Yes | Yes |
| View matched expert details | **No** | **Yes** | N/A | N/A | Yes | Yes |
| Book consultation | **No** | **Yes** | N/A | N/A | Yes | Yes |
| View booking details | **No** | **Yes** | N/A | N/A | Yes | Yes |
| Access messaging | **No** | **Yes** | N/A | N/A | Yes | Yes |
| Leave review | **No** | **Yes** | N/A | N/A | Yes | Yes |
| Account settings | Yes | Yes | Yes | Yes | Yes | Yes |

#### Authenticated expert pages

| Page/Action | Unverified client | Verified client | Applied expert | Vetted/Active expert | Ops admin | Super admin |
|-------------|-------------------|-----------------|----------------|----------------------|-----------|-------------|
| Expert dashboard | N/A | N/A | Yes | Yes | Yes | Yes |
| Profile wizard | N/A | N/A | Yes | Yes | Yes | Yes |
| Edit own profile | N/A | N/A | Yes | Yes | Yes | Yes |
| View availability calendar | N/A | N/A | No | Yes | Yes | Yes |
| Manage availability slots | N/A | N/A | No | **Vetted/Active only** | Yes | Yes |
| View incoming bookings | N/A | N/A | No | **Vetted/Active only** | Yes | Yes |
| Accept/decline bookings | N/A | N/A | No | **Active only** | Yes | Yes |
| Access messaging | N/A | N/A | No | **Vetted/Active only** | Yes | Yes |
| View earnings | N/A | N/A | No | **Active only** | Yes | Yes |

#### Admin pages

| Page/Action | Unverified client | Verified client | Applied expert | Vetted/Active expert | Ops admin | Super admin |
|-------------|-------------------|-----------------|----------------|----------------------|-----------|-------------|
| Django admin panel | No | No | No | No | Yes | Yes |
| User management | No | No | No | No | Yes | Yes |
| Expert application review | No | No | No | No | Yes | Yes |
| Expert profile vetting | No | No | No | No | Yes | Yes |
| Booking management | No | No | No | No | Yes | Yes |
| Payment management | No | No | No | No | Limited | Yes |
| System configuration | No | No | No | No | No | Yes |
| Audit log access | No | No | No | No | Read-only | Full |

---

## 2. Client onboarding flow

### 2.1 Entry points

Clients can begin onboarding through three primary entry points:

1. **Homepage CTA** - "Get started" or "Find an expert" button
2. **Contact page** - Contact form submission creates initial enquiry
3. **Request form** - Direct access to consultation request submission

### 2.2 Registration flow

```
Step 1: User lands on entry point
    |
Step 2: Clicks sign up / submits request form
    |
Step 3: Registration form displayed
    |
Step 4: User completes registration
    |
Step 5: Account created (unverified)
    |
Step 6: Verification email sent
    |
Step 7: User clicks verification link
    |
Step 8: Email verified (verified_client)
    |
Step 9: Full platform access granted
```

### 2.3 Data collected at registration

| Field | Required | Validation |
|-------|----------|------------|
| Email address | Yes | Valid email format, unique in system |
| First name | Yes | Max 100 characters |
| Last name | Yes | Max 100 characters |
| Password | Yes | Minimum 8 characters, Django password validators |
| Password confirmation | Yes | Must match password |
| Privacy consent | Yes | Must be checked (POPIA compliance) |
| Terms acceptance | Yes | Must be checked |

### 2.4 Data collected at consultation request

| Field | Required | Validation |
|-------|----------|------------|
| Name | Yes | Max 200 characters |
| Company | Yes | Max 200 characters |
| Email | Yes | Valid email format |
| Phone | No | Max 30 characters |
| Problem description | Yes | Text field (no limit) |
| Engagement type | Yes | consultation / research / advisory |
| Timeline urgency | Yes | low / medium / high / critical |
| Budget range | No | Max 100 characters |
| Brief document | No | PDF/DOCX, max 10MB |
| POPIA consent | Yes | Must be checked |
| Confidentiality level | Yes | standard / elevated / strict |
| Preferred expertise tags | No | Multiple selection |

### 2.5 Submission status definitions

When a client submits a consultation request, it receives the following statuses:

| Status | Database value | Meaning |
|--------|----------------|---------|
| Pending review | `pending` | Initial state, awaiting admin review |
| In review | `in_review` | Admin actively reviewing the request |
| Expert matched | `matched` | Admin has identified suitable expert(s) |
| Proposal sent | `proposal_sent` | Engagement proposal sent to client |
| Confirmed | `confirmed` | Client accepted proposal, booking created |
| In progress | `in_progress` | Consultation underway |
| Completed | `completed` | Engagement finished |
| Cancelled | `cancelled` | Request cancelled by client or admin |
| Expired | `expired` | Request expired without action |

### 2.6 Admin review criteria

When reviewing a client request, admins must assess:

1. **Legitimacy check**
   - Company name is verifiable (web search, LinkedIn)
   - Email domain matches company (not generic Gmail/Yahoo for corporate requests)
   - Problem description is coherent and specific

2. **Scope assessment**
   - Engagement type is appropriate for described problem
   - Timeline is realistic for the scope
   - Budget range (if provided) aligns with engagement complexity

3. **Expertise matching**
   - Requested expertise areas exist in expert pool
   - Available experts have capacity for timeline
   - Confidentiality requirements can be met

4. **Compliance verification**
   - POPIA consent is recorded
   - No prohibited content in request description
   - Brief document (if uploaded) is appropriate

5. **Risk assessment**
   - No indicators of fraudulent activity
   - Payment capability assessment (for high-value engagements)

### 2.7 Verification trigger points

| Event | Trigger | Result |
|-------|---------|--------|
| Account creation | User completes sign-up form | `email_verified=False`, verification email sent |
| Email verification | User clicks verification link | `email_verified=True` |
| Portal access grant | `email_verified=True` | Full client functionality unlocked |
| Expert list visibility | `email_verified=True` | Semi-private expert profiles visible |

**Critical rule:** The exact point at which portal access is granted is when `email_verified=True` is set on the user record after clicking the verification link.

**Critical rule:** The exact point at which the expert list (including semi-private profiles) becomes visible is when `email_verified=True`. Unverified clients can only see public profiles.

### 2.8 UX messaging

#### Before email verification

| Context | Message |
|---------|---------|
| Post-registration | "Welcome to Kairos! Your account has been created. Please check your email to verify your account." |
| Dashboard (unverified) | "Your email address has not been verified. Some features are limited until you verify your email. [Resend verification email]" |
| Attempting restricted action | "This feature requires email verification. Please verify your email to continue." |
| Viewing expert directory | "You are viewing public expert profiles only. Verify your email to see more experts." |

#### After email verification

| Context | Message |
|---------|---------|
| Email verified | "Your email has been verified. You now have full access to the platform." |
| Dashboard (verified) | Standard dashboard with full functionality |
| Expert directory | Full directory access including semi-private profiles |

---

## 3. Expert onboarding gate

### 3.1 Application via careers form

Experts apply through the "Join as expert" page (`/experts/join/`):

```
Step 1: Visitor navigates to careers/join page
    |
Step 2: Completes expert application form
    |
Step 3: Application submitted (status: pending)
    |
Step 4: Admin reviews application
    |
Step 5a: Approved -> Invitation to create account sent
    |
Step 5b: Rejected -> Rejection notification sent
    |
Step 6: Expert creates account (role: expert)
    |
Step 7: Expert completes profile wizard
    |
Step 8: Profile submitted for vetting
    |
Step 9: Admin vets profile and credentials
    |
Step 10: Expert receives vetted/active status
```

### 3.2 Application form data collected

| Field | Required | Validation |
|-------|----------|------------|
| Full name | Yes | Max 200 characters |
| Email | Yes | Valid email format |
| Phone | No | Max 50 characters |
| LinkedIn URL | No | Valid URL format |
| GitHub URL | No | Valid URL format |
| ORCID ID | No | Max 50 characters, format 0000-0000-0000-0000 |
| Expertise areas | Yes | Text description |
| Years of experience | No | Selection: 3-5, 5-10, 10-15, 15-20, 20+ |
| Bio | No | Text field |
| CV file | No | PDF/DOC/DOCX, max 10MB |
| POPIA consent | Yes | Must be checked |

### 3.3 Application status definitions

| Status | Database value | Meaning |
|--------|----------------|---------|
| Pending review | `pending` | Application awaiting admin review |
| Approved | `approved` | Application accepted, invitation sent |
| Rejected | `rejected` | Application declined |

### 3.4 Profile wizard steps

Once an expert account is created, they complete a 6-step wizard:

| Step | Content | Required fields |
|------|---------|-----------------|
| 1 - Basic info | Headline, bio, pronouns, affiliation, location | Headline |
| 2 - Avatar | Profile photo upload | No |
| 3 - Expertise | Expertise tags, sector expertise | At least one tag |
| 4 - Experience | Years experience, senior roles, languages | Years experience |
| 5 - Verification | Upload verification documents (ID, qualifications) | At least one document |
| 6 - Confirmation | Review and submit for vetting | Confirmation click |

### 3.5 Verification status definitions

| Status | Database value | Meaning | Matchable | Visible in directory |
|--------|----------------|---------|-----------|---------------------|
| Applied | `applied` | Profile wizard completed, awaiting vetting | No | No |
| Vetted | `vetted` | Background verified, profile approved | Yes | Yes (if `is_publicly_listed=True`) |
| Active | `active` | Fully operational, can receive bookings | Yes | Yes (if `is_publicly_listed=True`) |
| Needs changes | `needs_changes` | Admin requires profile corrections | No | No |
| Rejected | `rejected` | Profile/credentials rejected | No | No |

### 3.6 Becoming matchable and visible

**Critical rule:** An expert becomes matchable when:
- `verification_status` is `vetted` OR `active`
- Admin can match them to client requests

**Critical rule:** An expert becomes visible in the directory when:
- `verification_status` is `vetted` OR `active`
- `is_publicly_listed=True`
- `privacy_level` determines who can see them (see section 4)

---

## 4. Expert list access rules

### 4.1 Privacy levels

Each expert profile has a `privacy_level` setting:

| Level | Database value | Visible to |
|-------|----------------|------------|
| Public | `public` | Everyone (including anonymous visitors) |
| Semi-private | `semi_private` | Verified clients, profile owner, admins |
| Private | `private` | Profile owner and admins only |

### 4.2 Directory visibility matrix

| Viewer type | Public experts | Semi-private experts | Private experts |
|-------------|----------------|----------------------|-----------------|
| Anonymous visitor | Yes | **No** | No |
| Unverified client | Yes | **No** | No |
| Verified client | Yes | **Yes** | No |
| Applied expert | Yes | No | No |
| Vetted/Active expert | Yes | Yes (own profile only) | Own profile only |
| Ops admin | Yes | Yes | Yes |
| Super admin | Yes | Yes | Yes |

### 4.3 Access enforcement

The directory view (`/experts/`) implements the following logic:

```python
base_query = ExpertProfile.objects.filter(
    verification_status__in=['vetted', 'active'],
    is_publicly_listed=True,
)

if is_verified_client or is_admin:
    experts = base_query.filter(privacy_level__in=['public', 'semi_private'])
else:
    experts = base_query.filter(privacy_level='public')
```

### 4.4 What unverified clients see

Unverified clients accessing the expert directory:
- See only experts with `privacy_level='public'`
- Cannot see individual expert names for semi-private/private profiles
- See a prompt encouraging email verification to view more experts
- Cannot view semi-private profile details even via direct URL

### 4.5 What verified clients see

Verified clients accessing the expert directory:
- See all experts with `privacy_level` of `public` or `semi_private`
- Can view full profile details for these experts
- Cannot see private profiles (these are admin-matched only)

### 4.6 Profile access enforcement

Individual profile pages (`/experts/<uuid>/`) enforce:

| Profile privacy | Anonymous/Unverified | Verified client | Profile owner | Admin |
|-----------------|---------------------|-----------------|---------------|-------|
| Public | View allowed | View allowed | View allowed | View allowed |
| Semi-private | Redirect to directory + error | View allowed | View allowed | View allowed |
| Private | Redirect to directory + error | Redirect to directory + error | View allowed | View allowed |

Error messages:
- Semi-private (unverified): "This expert profile requires email verification to view. Please verify your email address."
- Private (non-owner): "This expert profile is private."

### 4.7 Directory model options

The platform supports two directory models:

**Option A: Gated directory (current implementation)**
- Public profiles visible to all
- Semi-private profiles visible only to verified clients
- Private profiles never shown in directory (admin-matched only)

**Option B: Capabilities page + matched shortlists (alternative)**
- Remove public directory entirely
- Replace with a capabilities/services page describing expertise areas
- Clients submit requests, admins curate shortlists
- Shortlists sent to verified clients only

If Option B is implemented:
- Remove `/experts/` directory route
- Create `/capabilities/` page with expertise categories
- Client requests result in curated shortlist (3-5 experts)
- Shortlist visible in client dashboard after admin matching

---

## 5. Demo account expectations

### 5.1 Required demo accounts

The following demo accounts must exist for testing and demonstration:

| Account | Email | Role | State | Password |
|---------|-------|------|-------|----------|
| Demo client (unverified) | demo.client.unverified@kairos-test.co.za | client | email_verified=False | [Set in secrets] |
| Demo client (verified) | demo.client@kairos-test.co.za | client | email_verified=True | [Set in secrets] |
| Demo expert (applied) | demo.expert.applied@kairos-test.co.za | expert | verification_status='applied' | [Set in secrets] |
| Demo expert (active) | demo.expert@kairos-test.co.za | expert | verification_status='active' | [Set in secrets] |
| Demo ops admin | demo.ops@kairos-test.co.za | admin | is_staff=True, is_superuser=False | [Set in secrets] |
| Demo super admin | demo.admin@kairos-test.co.za | admin | is_staff=True, is_superuser=True | [Set in secrets] |

### 5.2 Demo account behaviour

#### Demo unverified client
- Can access: Homepage, about, services, contact, blog, sign up, log in
- Can access: Client dashboard (with verification warning banner)
- Can access: Expert directory (public profiles only)
- Cannot access: Booking functionality, messaging, matched expert details
- Shows: Verification prompt on restricted actions

#### Demo verified client
- Can access: All public pages
- Can access: Full client dashboard, request submission, booking
- Can access: Expert directory (public + semi-private profiles)
- Can access: Messaging with matched experts
- Shows: Standard verified user experience

#### Demo applied expert
- Can access: All public pages
- Can access: Expert dashboard (limited)
- Can access: Profile wizard (to complete or edit)
- Cannot access: Availability management, booking management
- Shows: "Profile under review" status banner

#### Demo active expert
- Can access: All public pages
- Can access: Full expert dashboard
- Can access: Own profile, availability management
- Can access: Booking management, messaging, earnings view
- Shows: Standard active expert experience

#### Demo ops admin
- Can access: All public pages
- Can access: Django admin panel
- Can access: User management, expert vetting, booking management
- Cannot access: System configuration, payment settings (full)
- Shows: Limited admin interface

#### Demo super admin
- Can access: All pages and functionality
- Can access: Full Django admin panel
- Can access: All management features, system configuration
- Shows: Full admin interface

### 5.3 Demo data requirements

Each demo account should have associated test data:
- Demo verified client: 2-3 historical requests in various statuses
- Demo active expert: Complete profile, availability slots, 2-3 bookings
- Admin accounts: Access to review queues with pending items

---

## 6. Ready to implement checklist

### 6.1 User model updates

- [ ] Confirm `email_verified` field exists on User model
- [ ] Confirm `email_verification_token` field exists for verification flow
- [ ] Add email verification view if not present
- [ ] Add verification email sending on registration

### 6.2 Client onboarding

- [ ] Implement email verification flow (send, validate, update flag)
- [ ] Add verification status banner to client dashboard
- [ ] Gate booking functionality behind `email_verified=True`
- [ ] Gate messaging functionality behind `email_verified=True`
- [ ] Gate matched expert details behind `email_verified=True`
- [ ] Add "resend verification email" functionality

### 6.3 Expert onboarding

- [ ] Confirm ExpertApplication model and form exist
- [ ] Implement application status workflow (pending -> approved/rejected)
- [ ] Add invitation email flow for approved applications
- [ ] Confirm profile wizard 6-step flow is complete
- [ ] Gate expert features behind `verification_status` checks

### 6.4 Expert directory access

- [ ] Implement privacy level filtering in directory view
- [ ] Add verification check for semi-private profile access
- [ ] Add appropriate error messages for access denials
- [ ] Add "verify email to see more" prompt for unverified clients

### 6.5 Admin features

- [ ] Confirm admin can change user verification status
- [ ] Confirm admin can change expert verification status
- [ ] Add bulk actions for application review
- [ ] Add audit logging for all status changes

### 6.6 Demo accounts

- [ ] Create management command for demo account setup
- [ ] Add demo data fixtures for each account type
- [ ] Document demo account credentials in secure location
- [ ] Ensure demo accounts reset to known state for demos

### 6.7 Testing requirements

- [ ] Unit tests for permission checks on all protected views
- [ ] Integration tests for email verification flow
- [ ] Integration tests for expert application workflow
- [ ] End-to-end tests for client onboarding journey
- [ ] End-to-end tests for expert onboarding journey

---

## Appendix A: Database field reference

### User model fields (access control)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| role | CharField | 'client' | Primary role assignment |
| email_verified | BooleanField | False | Email verification status |
| is_staff | BooleanField | False | Django admin access |
| is_superuser | BooleanField | False | Full permissions |
| is_active | BooleanField | True | Account enabled |

### ExpertProfile fields (visibility control)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| verification_status | CharField | 'applied' | Vetting progress |
| privacy_level | CharField | 'semi_private' | Directory visibility |
| is_publicly_listed | BooleanField | True | Show in directory |
| is_featured | BooleanField | False | Homepage feature |

---

## Appendix B: Audit events

All access control changes must be logged:

| Event type | Trigger |
|------------|---------|
| USER_CREATED | New user registration |
| USER_LOGIN | Successful login |
| PROFILE_UPDATED | Profile changes |
| VERIFICATION_STATUS_CHANGED | Expert status change |
| ADMIN_ACTION | Admin performs action |

---

*End of specification*
