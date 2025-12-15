# Kairos - Expert Consultation Platform

## Overview
Kairos is a SaaS platform connecting clients with verified PhD experts, professors, and industry specialists for premium consultations. The platform emphasises brilliance, expertise, and global service capability.

## Recent Changes
- **December 2024**: Redesigned UI with elegant black/white color scheme and gold accent color
- **December 2024**: Created new "Careers" page with domain/expertise/skill-based search
- **December 2024**: Removed pricing visibility from public pages (shown after consultation)
- **December 2024**: Updated navigation structure and messaging to emphasise expert brilliance
- **December 2024**: Added comprehensive AWS deployment documentation in README.md

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
- `templates/experts/careers.html` - Main expert search page (skill-based)
- `templates/experts/profile.html` - Expert profile (pricing hidden until consultation)

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
