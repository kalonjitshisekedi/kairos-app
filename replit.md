# Kairos - Expert Consultation Platform

## Overview

Kairos is a premium expert consultation platform where clients book and pay to speak with verified PhD and postdoc experts. The platform features British English throughout, uses sentence case for UI elements, and displays the tagline "don't guess. know".

## Current state

The MVP is complete with all core features implemented:
- User authentication and role-based access (clients, experts, admins)
- Expert profile system with verification workflow
- Expert directory with search and filtering
- Booking flow with availability management
- Session rooms with Jitsi video integration
- Messaging system between clients and experts
- Stripe payment integration (test mode)
- Admin operations dashboard
- POPIA-compliant privacy features

## Project architecture

### Django apps

| App | Purpose |
|-----|---------|
| `accounts` | Custom user model, authentication, profile settings |
| `experts` | Expert profiles, verification, expertise tags |
| `availability` | Weekly schedules, time slots, blocked dates |
| `consultations` | Bookings, reviews, concierge requests |
| `messaging` | Message threads between clients and experts |
| `payments` | Stripe integration, invoices, payouts |
| `core` | Homepage, search, legal pages, admin dashboard |

### Key files

- `kairos/settings.py` - Django settings with environment variables
- `kairos/urls.py` - URL routing configuration
- `templates/base.html` - Base template with Bootstrap 5
- `core/context_processors.py` - Site-wide template variables

### Database

PostgreSQL database using Replit's built-in database. Models use UUIDs as primary keys.

## Running the project

### Development

The server runs automatically via the configured workflow:
```bash
python manage.py runserver 0.0.0.0:5000
```

### Management commands

```bash
# Run migrations
python manage.py migrate

# Seed sample data
python manage.py seed_data

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (auto-set) |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enable debug mode (default: True) |
| `PAYMENTS_ENABLED` | Enable Stripe payments (default: False) |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key |
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |

## Test accounts

After running `python manage.py seed_data`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@kairos.example.com | admin123 |
| Expert | dr.smith@kairos.example.com | expert123 |
| Expert | dr.chen@kairos.example.com | expert123 |
| Client | client1@example.com | client123 |

## Features

### For clients
- Browse verified expert directory
- Search by expertise, industry, price range
- Book consultations with calendar picker
- Submit concierge requests for admin matching
- Join video sessions via Jitsi
- Leave reviews and ratings

### For experts
- Profile wizard for onboarding
- Set rates for 30/60/90 minute sessions
- Manage weekly availability
- Block specific dates
- Accept/decline booking requests
- Private notes during sessions
- Upload deliverables

### For admins
- Verify expert credentials
- Match concierge requests
- View upcoming sessions
- Access audit log
- Django admin interface

## Design choices

- **British English**: All UI text uses British spelling (organisation, favour)
- **Sentence case**: UI elements use sentence case, not title case
- **Jitsi**: Embedded video by default, with external link fallback
- **POPIA compliance**: Data minimisation, explicit consent, deletion requests
- **Stripe test mode**: Payments can be toggled via environment variable

## Recent changes

- 15 Dec 2024: Initial MVP complete
  - All 7 Django apps implemented
  - 40+ templates created
  - Database migrations applied
  - Seed data command added
