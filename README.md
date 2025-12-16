# Kairos - Expert Consultation Platform

A professional SaaS platform connecting clients with verified PhD experts, professors, and industry specialists for premium consultations.

## Overview

Kairos provides a curated marketplace where clients can access brilliant minds with deep domain knowledge. The platform serves global clients while maintaining strict verification standards for all experts.

### Key Features

- **Expert Directory**: Browse verified experts by domain, expertise, and skills
- **Consultation Booking**: Request and schedule private video consultations
- **Concierge Matching**: Submit requests for personalised expert recommendations
- **Expert Verification**: Rigorous credential verification workflow
- **Secure Payments**: Integrated payment processing via Stripe
- **Messaging System**: Private communication between clients and experts

## Technology Stack

- **Backend**: Django 5.x with Django REST Framework
- **Database**: PostgreSQL
- **File Storage**: AWS S3 (via django-storages)
- **Payments**: Stripe
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

| Role | Email | Password |
|------|-------|----------|
| Super admin | admin@kairos.co.za | KairosAdmin123! |
| Operations (staff) | ops@kairos.co.za | KairosOps123! |
| Client | client@kairos.co.za | KairosClient123! |
| Expert | dr.molefe@kairos.co.za | KairosExpert123! |

### What gets created

**Users:**
- Super admin with full access
- Operations user (staff only, no superuser)
- Client user (Morgan Naidoo from Umkhonto Capital)
- Expert user (Naledi Mbeki with 18 years fintech/risk experience)

**Content:**
- 3 published blog posts
- 1 pending client request
- 1 matched/scheduled engagement
- 1 ongoing engagement (in progress)
- 1 completed engagement with review

### Quick click-through test checklist

**Public pages:**
1. Home → Blog (should show 3 posts)
2. Home → Why Kairos
3. Home → Contact us (should show contact@kairos.co.za)
4. Verify navbar shows: Log in → Create an account → Submit a request

**Admin workflow:**
1. Log in as admin@kairos.co.za
2. Access Django admin at `/admin/`
3. View and manage blog posts
4. Access Operations dashboard at `/operations/`

**Client workflow:**
1. Log in as client@kairos.co.za
2. Submit a request via "Submit a request" button
3. View dashboard and existing requests/engagements

**Expert workflow:**
1. Log in as dr.molefe@kairos.co.za
2. Access expert dashboard (shows assigned engagements)
3. View profile and availability settings

## Support

For technical issues or questions, contact the development team.

## Licence

Proprietary - All rights reserved.
