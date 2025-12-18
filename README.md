# Kairos - Expert Consultation Platform

A professional SaaS platform connecting clients with verified PhD experts, professors, and industry specialists for premium consultations.

## Overview

Kairos provides a curated marketplace where clients can access brilliant minds with deep domain knowledge. The platform serves global clients while maintaining strict verification standards for all experts.

### Key Features

- **Expert Catalogue**: Gated directory of verified experts accessible to authenticated clients
- **Request Matching**: Submit consultation requests for expert matching by admin
- **Engagement Management**: End-to-end workflow from request submission to completion
- **Expert Verification**: Rigorous credential verification with profile uploads (CV, professional links)
- **Invoice-based Payments**: Payment handling via invoicing system (no card checkout)
- **Messaging System**: Private communication between clients and experts within booking context

## Current Platform Workflow (Implemented)

### Access Control
The platform uses role-based gating with `client_status` and `expert_status` fields:
- **Verified clients** can access the expert catalogue and submit consultation requests
- **Unverified clients** see public expert profiles only
- **Experts** must be verified (active status) to receive and manage bookings
- **Admins** (ops staff and superusers) manage expert vetting and client matching

### Expert Catalogue
Located at `/experts/catalogue/`:
- Accessible to: verified clients, staff, and admin users
- Shows: vetted/active experts with public or semi-private profiles
- Each expert displays: headline, bio, expertise tags, years of experience, affiliation
- Features: "Request this expert" button for direct engagement initiation

### Request → Match → Engagement → Completion Flow
1. **Client submits request** - Fills form with problem description, engagement type, urgency, budget
2. **Admin reviews and matches** - Ops staff identifies suitable expert(s) from catalogue
3. **Expert receives notification** - Invitation to accept/decline the engagement
4. **Proposal sent to client** - Admin creates invoice with pricing and scope
5. **Engagement confirmed** - Client accepts terms; invoice sent for payment
6. **Expert delivery** - Work progresses; expert marks complete when done
7. **Client confirmation** - Client confirms satisfaction; payout becomes eligible
8. **Completion and review** - Engagement archived; client may leave review

### Invoice-based Payment Model
- No card checkout at platform level
- Admin creates and sends invoices after client accepts proposal
- Client pays via bank transfer or EFT
- Expert payout triggered after completion confirmed and payment received
- Platform retains fee between invoiced amount and expert payout rate

### Expert Profile Management
- **Edit page** (`/experts/edit/`): Experts can update profile with complete information:
  - Basic info (headline, bio, pronouns, affiliation, location, timezone)
  - Profile photo upload (JPG/PNG/GIF, max 5MB)
  - CV upload (PDF/DOCX, max 10MB)
  - Professional links (LinkedIn, GitHub, ORCID URLs)
  - Expertise areas and tags selection
  - Languages and availability settings
  - Profile visibility (public/semi-private/private)

## Technology Stack

- **Backend**: Django 5.x with Django REST Framework
- **Database**: PostgreSQL
- **File Storage**: AWS S3 (via django-storages) + local media in development
- **Payments**: Invoice-based (no Stripe card processing)
- **Frontend**: Bootstrap 5 with custom styling

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for frontend assets, if applicable)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kairos
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# Or if using uv:
uv sync
```

4. Configure environment variables (see Environment Variables section below)

5. Run database migrations:
```bash
python manage.py migrate
```

6. Create a superuser (admin account):
```bash
python manage.py createsuperuser
```

7. (Optional) Seed sample data:
```bash
python manage.py seed_data
```

8. Start the development server:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kairos

# AWS S3 Configuration (for file uploads)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=eu-west-1

# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@kairos.com
```

## AWS Deployment

### Prerequisites

- AWS Account with appropriate IAM permissions
- AWS CLI configured locally
- Domain name (optional but recommended)

### Infrastructure Setup

#### 1. Create an RDS PostgreSQL Database

```bash
aws rds create-db-instance \
    --db-instance-identifier kairos-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15 \
    --master-username kairosadmin \
    --master-user-password <secure-password> \
    --allocated-storage 20 \
    --vpc-security-group-ids <your-security-group> \
    --publicly-accessible
```

After creation, note the endpoint URL for your DATABASE_URL.

#### 2. Create an S3 Bucket for Media Files

```bash
aws s3 mb s3://kairos-media-<unique-suffix> --region eu-west-1

# Configure CORS for the bucket
aws s3api put-bucket-cors --bucket kairos-media-<unique-suffix> --cors-configuration '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}'
```

#### 3. Create an IAM User for S3 Access

Create an IAM user with the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::kairos-media-*",
                "arn:aws:s3:::kairos-media-*/*"
            ]
        }
    ]
}
```

### Deployment Options

#### Option A: AWS Elastic Beanstalk

1. Install the EB CLI:
```bash
pip install awsebcli
```

2. Initialise the application:
```bash
eb init -p python-3.11 kairos
```

3. Create the environment:
```bash
eb create kairos-production
```

4. Set environment variables:
```bash
eb setenv SECRET_KEY=<your-secret-key> \
    DATABASE_URL=<your-rds-url> \
    AWS_ACCESS_KEY_ID=<your-key> \
    AWS_SECRET_ACCESS_KEY=<your-secret> \
    AWS_STORAGE_BUCKET_NAME=<your-bucket> \
    STRIPE_SECRET_KEY=<your-stripe-key>
```

5. Deploy:
```bash
eb deploy
```

#### Option B: AWS ECS with Fargate

1. Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "kairos.wsgi:application"]
```

2. Build and push to ECR:
```bash
aws ecr create-repository --repository-name kairos
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t kairos .
docker tag kairos:latest <account>.dkr.ecr.<region>.amazonaws.com/kairos:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/kairos:latest
```

3. Create ECS cluster and service using the AWS Console or CloudFormation.

#### Option C: EC2 with Nginx

1. Launch an EC2 instance (Ubuntu 22.04 recommended)

2. SSH into the instance and install dependencies:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql-client
```

3. Clone and set up the application:
```bash
git clone <repository-url> /var/www/kairos
cd /var/www/kairos
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

4. Create systemd service (`/etc/systemd/system/kairos.service`):
```ini
[Unit]
Description=Kairos Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kairos
Environment="PATH=/var/www/kairos/venv/bin"
EnvironmentFile=/var/www/kairos/.env
ExecStart=/var/www/kairos/venv/bin/gunicorn --workers 3 --bind unix:/var/www/kairos/kairos.sock kairos.wsgi:application

[Install]
WantedBy=multi-user.target
```

5. Configure Nginx (`/etc/nginx/sites-available/kairos`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/kairos/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/kairos/kairos.sock;
    }
}
```

6. Enable and start services:
```bash
sudo systemctl enable kairos
sudo systemctl start kairos
sudo ln -s /etc/nginx/sites-available/kairos /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Post-Deployment Steps

1. Run migrations on the production database:
```bash
python manage.py migrate
```

2. Create an admin superuser:
```bash
python manage.py createsuperuser
```

3. Collect static files:
```bash
python manage.py collectstatic --noinput
```

4. Configure Stripe webhooks in the Stripe Dashboard to point to:
```
https://your-domain.com/payments/webhook/
```

## Cost-Effective AWS Deployment Guide

This section provides recommendations for deploying Kairos on AWS in the most cost-effective way for a South African startup.

### Estimated Monthly Costs (USD)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| RDS PostgreSQL | db.t3.micro (Free Tier eligible) | $0 - $15/month |
| S3 Storage | 10GB with minimal requests | $0.25/month |
| EC2 (if used) | t3.micro (Free Tier eligible) | $0 - $8/month |
| Elastic Beanstalk | Uses underlying EC2 | $8 - $20/month |
| CloudFront (optional) | 50GB transfer | $5/month |
| **Total (startup phase)** | | **$15 - $50/month** |

### Cost Optimisation Tips

1. **Use AWS Free Tier**: New accounts get 12 months of free tier including:
   - 750 hours/month of t3.micro EC2
   - 750 hours/month of db.t3.micro RDS
   - 5GB S3 storage

2. **Choose af-south-1 (Cape Town)**: For South African users, this region offers lowest latency. Note: Free Tier may not apply to all services in this region.

3. **Use Reserved Instances**: After testing, commit to 1-year reserved instances for 30-40% savings.

4. **S3 Lifecycle Policies**: Move old files to S3 Glacier for 90% storage savings:
```bash
aws s3api put-bucket-lifecycle-configuration --bucket kairos-media \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "ArchiveOldFiles",
      "Status": "Enabled",
      "Filter": {"Prefix": ""},
      "Transitions": [{
        "Days": 90,
        "StorageClass": "GLACIER"
      }]
    }]
  }'
```

5. **Use Spot Instances for Dev/Test**: Save up to 90% on development environments.

6. **RDS Cost Savings**:
   - Use db.t3.micro for development
   - Enable storage auto-scaling to avoid over-provisioning
   - Consider Aurora Serverless for variable workloads

### Recommended Architecture (Budget-Friendly)

For a startup with low to moderate traffic:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Route 53  │────▶│ CloudFront  │────▶│    S3       │
│   (Domain)  │     │    (CDN)    │     │ (Static)    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   ALB/EB    │
                    │ (Load Bal)  │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  EC2/EB     │────▶│  RDS        │
                    │ (App Server)│     │ (PostgreSQL)│
                    └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    S3       │
                    │  (Media)    │
                    └─────────────┘
```

### Alternative: Deploy on Replit

For the most cost-effective approach during early stages, deploy directly on Replit:
- Built-in PostgreSQL database
- Automatic HTTPS and domain
- Zero DevOps overhead
- Pay-as-you-go pricing

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific app tests
pytest accounts/tests.py
pytest experts/tests.py
```

### Cross-Platform Testing

#### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip postgresql-client

# Clone and setup
git clone <repository-url>
cd kairos
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations and tests
python manage.py migrate
pytest

# Start development server
python manage.py runserver 0.0.0.0:5000
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and PostgreSQL
brew install python@3.11 postgresql@15

# Clone and setup
git clone <repository-url>
cd kairos
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations and tests
python manage.py migrate
pytest

# Start development server
python manage.py runserver 0.0.0.0:5000
```

#### Windows (PowerShell)

```powershell
# Install Python 3.11 from python.org or via winget
winget install Python.Python.3.11

# Install PostgreSQL (optional for local development)
winget install PostgreSQL.PostgreSQL

# Clone and setup
git clone <repository-url>
cd kairos
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings using notepad or VS Code

# Run migrations and tests
python manage.py migrate
pytest

# Start development server
python manage.py runserver 0.0.0.0:5000
```

### Test Database

Tests use a separate test database. Ensure your test settings use SQLite or a separate PostgreSQL database to avoid affecting development data.

## Account Creation Workflows

### Client Account Creation

1. Navigate to `/accounts/signup/`
2. Fill in email, name, and password
3. Verify email (if email verification is enabled)
4. Log in and browse experts

### Expert Account Creation

1. Navigate to `/accounts/signup/`
2. Select "I want to offer my expertise"
3. Complete the multi-step profile wizard:
   - Step 1: Basic information (name, headline, bio, affiliation)
   - Step 2: Upload professional photo
   - Step 3: Select expertise areas and tags
   - Step 4: Set consultation rates
   - Step 5: Upload verification documents
4. Submit profile for verification
5. Wait for admin approval

### Admin Account Setup

1. Create a superuser via command line:
```bash
python manage.py createsuperuser
```

2. Log in to the Django admin at `/admin/`

3. To grant admin privileges to an existing user:
   - Navigate to Accounts > Users
   - Select the user
   - Check "Is staff" and "Is admin"
   - Save

4. Admin users can access the Operations dashboard at `/operations/` to:
   - Verify expert profiles
   - Match concierge requests
   - View audit logs

## Project Structure

```
kairos/
├── accounts/          # User authentication and profiles
├── availability/      # Expert availability management
├── consultations/     # Booking and session management
├── core/              # Core views, admin dashboard
├── experts/           # Expert profiles and directory
├── messaging/         # Client-expert messaging
├── payments/          # Stripe integration
├── templates/         # HTML templates
├── static/            # Static assets
├── kairos/            # Django project settings
└── manage.py
```

## Security Considerations

- All sensitive data is stored as environment variables
- Passwords are hashed using Django's default PBKDF2 algorithm
- CSRF protection is enabled on all forms
- File uploads are validated and stored securely on S3
- Admin actions are logged in the audit trail

## Demo accounts and test data

### Seeding demo data

To create demo users and sample content for testing, run:

```bash
python manage.py migrate
python manage.py seed_demo
```

This command is idempotent and safe to run multiple times.

### Demo credentials

| Role | Email | Password | Account Status |
|------|-------|----------|-----------------|
| Super admin | admin@kairos.co.za | KairosAdmin123! | Full access, staff + superuser |
| Operations staff | ops@kairos.co.za | KairosOps123! | Staff only (can vet experts, match requests) |
| Verified client | client@kairos.co.za | KairosClient123! | Verified email, full client features |
| Active expert | dr.molefe@kairos.co.za | KairosExpert123! | Verified profile, can receive bookings |

### What gets created by seed_demo

**Users and Profiles:**
- 1 super admin with full platform access
- 1 operations staff user (can vet experts, match requests, manage platform)
- 1 verified client (Morgan Naidoo from Umkhonto Capital, email verified)
- 4 active expert profiles:
  - Dr Thabo Molefe: Computational biology, ML for drug discovery
  - Prof Nomvula Dlamini: Regulatory policy, financial systems
  - Dr Adaeze Okonkwo: Materials science, renewable energy
  - Dr Johan van Wyk: Quantitative finance, risk modeling
  - All have: CV uploaded, professional links, expertise tags, availability set

**Content:**
- 16 expertise tags (AI/ML, regulatory, finance, materials science, etc.)
- 3 published blog posts
- 1 pending client request
- 1 matched engagement (proposed, awaiting client confirmation)
- 1 completed engagement with review

### Quick click-through test checklist

**Public pages:**
1. Home → Blog (should show 3 posts)
2. Home → Why Kairos
3. Home → Expertise (new page showing expertise clusters)
4. Home → Contact us (should show contact@kairos.co.za)
5. Verify navbar shows: Why Kairos, How it works, For enterprise, Expertise, Blog, Contact us
6. Verify navbar CTAs: Log in → Create an account → Request expert matching

**Admin workflow:**
1. Log in as admin@kairos.co.za
2. Access Django admin at `/admin/`
3. View and manage blog posts
4. Access Operations dashboard at `/operations/`

**Client workflow:**
1. Log in as client@kairos.co.za
2. Submit a request via "Request expert matching" button
3. View dashboard and existing requests/engagements

**Expert workflow:**
1. Log in as dr.molefe@kairos.co.za
2. Visit `/experts/edit/` to manage profile with CV, professional links, expertise
3. Access expert dashboard (shows assigned engagements)
4. View availability settings and upcoming bookings

## Support

For technical issues or questions, contact the development team.

## Licence

Proprietary - All rights reserved.
