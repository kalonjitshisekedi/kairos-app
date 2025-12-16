# Kairos - Confidential Expert Network

## Overview
Kairos is a premium, confidential, enterprise-focused expert network. The platform enables enterprise clients to submit confidential requests which are matched by internal staff to vetted experts. Unlike public marketplaces, Kairos operates as a curated network with concierge-style matching.

**Tagline**: "Don't guess. Know."

## Recent Changes
- **December 2025**: Comprehensive premium UI redesign with dark luxury theme (#1a1a1a), gold accents (#c9a962), elegant serif typography
- **December 2025**: Implemented tiered privacy access controls: public (all), semi-private (verified clients only), private (admin-matched)
- **December 2025**: Semi-private access now requires email_verified=True on client accounts
- **December 2025**: Expert directory shows access restriction notice for unauthenticated users
- **December 2025**: Updated 15+ templates with premium styling and concierge-led language
- **December 2024**: Transformed platform from public marketplace to enterprise-focused expert network
- **December 2024**: Removed hourly rates; pricing is now per-engagement negotiated by Kairos team
- **December 2024**: Added privacy levels for experts (public, semi-private, private)
- **December 2024**: Changed verification workflow: applied → vetted → active
- **December 2024**: Created ClientRequest model for enterprise request submission
- **December 2024**: Updated all templates with enterprise positioning and confidentiality messaging
- **December 2024**: Added submit_client_request view for concierge-style client flow
- **December 2024**: Updated navigation: Submit request, How it works, For enterprise, Expert network

## Platform Model

### For Enterprise Clients
1. Submit a confidential request describing their challenge
2. Kairos team reviews and matches with ideal expert(s)
3. Engagement is coordinated through Kairos with NDA options
4. Pricing negotiated per engagement (not hourly marketplace rates)

### For Experts
1. Apply via expert network application form
2. Vetted by Kairos team (applied → vetted → active)
3. Matched with client requests by Kairos staff
4. Control profile visibility: public, semi-private, or private

### Privacy Levels
- **public**: Visible on directory to all visitors
- **semi_private**: Visible only to verified enterprise clients
- **private**: Not listed; matched manually by Kairos team only

### Service Types
- Consultation: Single expert consultation
- Advisory: Ongoing advisory relationship
- Project work: Project-based engagement
- Research: Research and analysis work

## Project Architecture

### Apps
- `accounts/` - User authentication, profiles, and account management
- `availability/` - Expert availability and time slot management
- `consultations/` - Client requests, bookings, sessions, and reviews
- `core/` - Landing pages, admin dashboard, and common views
- `experts/` - Expert profiles, directory, and vetting workflow
- `messaging/` - Private messaging between clients and experts
- `payments/` - Payment processing and expert payouts

### Key Models
- `ExpertProfile` - Expert with privacy_level, service_type, years_experience, verification_status (applied/vetted/active)
- `ClientRequest` - Enterprise client request with engagement_type, urgency, confidentiality level
- `Booking` - Engagement between client and expert with service_type

### Key Templates
- `templates/base.html` - Base template with global styling (black/white/gold theme)
- `templates/core/home.html` - Homepage with enterprise positioning
- `templates/consultations/submit_request.html` - Enterprise client request form
- `templates/experts/directory.html` - Expert directory (vetted experts only)
- `templates/experts/join.html` - Expert application form

### Design System
- **Primary colors**: Black (#0a0a0a), white (#fafafa)
- **Accent color**: Gold (#c9a962)
- **Typography**: Inter font family
- **Framework**: Bootstrap 5 with custom CSS variables

## Running the Project
```bash
python manage.py runserver 0.0.0.0:5000
```

## Database
PostgreSQL with migrations managed through Django ORM. Run migrations with:
```bash
python manage.py migrate
```

## User Preferences
- British English spelling throughout
- Proper sentence case capitalization
- No emoji usage
- Elegant, professional design aesthetic
- Enterprise-focused, confidentiality-first approach
