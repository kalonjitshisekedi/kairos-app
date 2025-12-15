"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from experts.models import ExpertProfile, ExpertiseTag

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seed data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        tags = self.create_expertise_tags()
        admin = self.create_admin_user()
        experts = self.create_sample_experts(tags)
        clients = self.create_sample_clients()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(f'  - {len(tags)} expertise tags')
        self.stdout.write(f'  - 1 admin user')
        self.stdout.write(f'  - {len(experts)} sample experts')
        self.stdout.write(f'  - {len(clients)} sample clients')

    def create_expertise_tags(self):
        disciplines = [
            ('Machine learning', 'machine-learning'),
            ('Data science', 'data-science'),
            ('Natural language processing', 'nlp'),
            ('Computer vision', 'computer-vision'),
            ('Biotechnology', 'biotechnology'),
            ('Pharmaceutical sciences', 'pharmaceutical'),
            ('Renewable energy', 'renewable-energy'),
            ('Climate science', 'climate-science'),
            ('Materials science', 'materials-science'),
            ('Neuroscience', 'neuroscience'),
            ('Economics', 'economics'),
            ('Finance', 'finance'),
            ('Law', 'law'),
            ('Policy analysis', 'policy-analysis'),
        ]
        
        industries = [
            ('Healthcare', 'healthcare'),
            ('Technology', 'technology'),
            ('Energy', 'energy'),
            ('Financial services', 'financial-services'),
            ('Manufacturing', 'manufacturing'),
            ('Consulting', 'consulting'),
            ('Education', 'education'),
        ]
        
        tags = []
        for name, slug in disciplines:
            tag, _ = ExpertiseTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'tag_type': 'discipline'}
            )
            tags.append(tag)
        
        for name, slug in industries:
            tag, _ = ExpertiseTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'tag_type': 'industry'}
            )
            tags.append(tag)
        
        return tags

    def create_admin_user(self):
        admin, created = User.objects.get_or_create(
            email='admin@kairos.example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'privacy_consent': True,
                'terms_accepted': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  Created admin: admin@kairos.example.com / admin123')
        return admin

    def create_sample_experts(self, tags):
        experts_data = [
            {
                'email': 'dr.smith@kairos.example.com',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'headline': 'Machine learning researcher specialising in NLP',
                'bio': 'Dr Sarah Smith is a leading researcher in natural language processing with over 10 years of experience. She has published extensively in top venues and consults for Fortune 500 companies on AI strategy.',
                'affiliation': 'University of Oxford',
                'location': 'Oxford, UK',
                'rate_30': 75,
                'rate_60': 140,
                'rate_90': 200,
            },
            {
                'email': 'dr.chen@kairos.example.com',
                'first_name': 'Wei',
                'last_name': 'Chen',
                'headline': 'Biotech entrepreneur and pharmaceutical scientist',
                'bio': 'Dr Wei Chen is a pharmaceutical scientist with experience in drug discovery and development. She has founded two successful biotech startups and holds multiple patents.',
                'affiliation': 'Imperial College London',
                'location': 'London, UK',
                'rate_30': 100,
                'rate_60': 180,
                'rate_90': 250,
            },
            {
                'email': 'dr.patel@kairos.example.com',
                'first_name': 'Raj',
                'last_name': 'Patel',
                'headline': 'Climate scientist and sustainability consultant',
                'bio': 'Dr Raj Patel is an expert in climate modelling and sustainable development. He advises governments and corporations on climate strategy and environmental policy.',
                'affiliation': 'University of Cambridge',
                'location': 'Cambridge, UK',
                'rate_30': 80,
                'rate_60': 150,
                'rate_90': 210,
            },
        ]
        
        experts = []
        for data in experts_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'expert',
                    'is_active': True,
                    'privacy_consent': True,
                    'terms_accepted': True,
                }
            )
            if created:
                user.set_password('expert123')
                user.save()
            
            profile, _ = ExpertProfile.objects.get_or_create(
                user=user,
                defaults={
                    'headline': data['headline'],
                    'bio': data['bio'],
                    'affiliation': data['affiliation'],
                    'location': data['location'],
                    'timezone': 'Europe/London',
                    'languages': ['English'],
                    'rate_30_min': data['rate_30'],
                    'rate_60_min': data['rate_60'],
                    'rate_90_min': data['rate_90'],
                    'verification_status': 'verified',
                    'is_publicly_listed': True,
                }
            )
            
            profile.expertise_tags.add(*tags[:3])
            experts.append(profile)
        
        return experts

    def create_sample_clients(self):
        clients_data = [
            {'email': 'client1@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'client2@example.com', 'first_name': 'Jane', 'last_name': 'Miller'},
        ]
        
        clients = []
        for data in clients_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'client',
                    'is_active': True,
                    'privacy_consent': True,
                    'terms_accepted': True,
                }
            )
            if created:
                user.set_password('client123')
                user.save()
            clients.append(user)
        
        return clients
