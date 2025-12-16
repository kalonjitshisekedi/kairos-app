# Kairos - Expert Consultation Platform

## Overview
Kairos is a SaaS platform connecting clients with verified PhD experts, professors, and industry specialists for premium consultations. The platform emphasises brilliance, expertise, and global service capability.

## Recent Changes
- **December 2024**: Added SVG logo and "Get In Touch" button in navbar
- **December 2024**: Created "Why Businesses Benefit" page for South African market context
- **December 2024**: Created "Get In Touch" contact page with POPIA-compliant form
- **December 2024**: Created "Join as Expert" careers page with CV upload, LinkedIn, GitHub, ORCID fields
- **December 2024**: Enhanced Expert Directory with "Vetted" badges and improved filtering
- **December 2024**: Added 10 dummy experts via seed_experts management command
- **December 2024**: Added ContactInquiry and ExpertApplication models
- **December 2024**: Redesigned UI with elegant black/white color scheme and gold accent color

## Project Architecture

### Apps
- `accounts/` - User authentication, profiles, and account management
- `availability/` - Expert availability and time slot management
- `consultations/` - Booking requests, sessions, and reviews
- `core/` - Landing pages, admin dashboard, and common views
- `experts/` - Expert profiles, directory, and verification workflow
- `messaging/` - Private messaging between clients and experts
- `payments/` - Stripe integration and payment processing

### Key Files
- `kairos/settings.py` - Django configuration
- `templates/base.html` - Base template with global styling (black/white/gold theme)
- `templates/experts/directory.html` - Expert directory with vetted badges and filters
- `templates/experts/join.html` - Expert application form (CV, LinkedIn, GitHub, ORCID)
- `templates/core/why_businesses.html` - Why businesses benefit page (South African context)
- `templates/core/contact.html` - Contact form with POPIA compliance
- `core/management/commands/seed_experts.py` - Seed 10 dummy experts

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
