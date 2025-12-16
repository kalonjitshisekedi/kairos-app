"""
Management command to seed 10 vetted dummy experts for demonstration.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User
from experts.models import ExpertProfile, ExpertiseTag


DUMMY_EXPERTS = [
    {
        "first_name": "Dr. Thabo",
        "last_name": "Molefe",
        "email": "thabo.molefe@example.com",
        "headline": "AI & Machine Learning Expert | PhD in Computer Science",
        "bio": "Dr. Thabo Molefe is a leading AI researcher with over 15 years of experience in machine learning and data science. He holds a PhD from the University of Cape Town and has published extensively in top-tier journals. Previously led AI initiatives at major South African banks.",
        "affiliation": "University of the Witwatersrand",
        "location": "Johannesburg, South Africa",
        "expertise": ["Artificial Intelligence", "Data Science"],
        "years_experience": 15,
        "rate_60_min": 2500,
        "linkedin": "https://linkedin.com/in/thabo-molefe",
        "orcid": "0000-0001-2345-6789",
        "credentials": "PhD Computer Science (UCT), MSc Data Science, Google Cloud Certified",
    },
    {
        "first_name": "Naledi",
        "last_name": "Khumalo",
        "email": "naledi.khumalo@example.com",
        "headline": "Financial Strategy Consultant | CFA Charterholder",
        "bio": "Naledi Khumalo is a seasoned financial strategist with expertise in corporate finance, M&A advisory, and investment analysis. She has advised JSE-listed companies and international investors on transactions exceeding R50 billion in value.",
        "affiliation": "Khumalo Advisory",
        "location": "Cape Town, South Africa",
        "expertise": ["Finance", "Strategy"],
        "years_experience": 12,
        "rate_60_min": 3000,
        "linkedin": "https://linkedin.com/in/naledi-khumalo",
        "orcid": "",
        "credentials": "CFA Charterholder, MBA (INSEAD), BCom Honours Finance (Stellenbosch)",
    },
    {
        "first_name": "Prof. James",
        "last_name": "van der Berg",
        "email": "james.vdberg@example.com",
        "headline": "Healthcare Innovation & Medical Research Expert",
        "bio": "Professor James van der Berg is a medical researcher specializing in healthcare innovation and clinical research methodology. He has led multi-center clinical trials and advises healthcare organizations on evidence-based practice implementation.",
        "affiliation": "University of Pretoria",
        "location": "Pretoria, South Africa",
        "expertise": ["Healthcare", "Research"],
        "years_experience": 20,
        "rate_60_min": 3500,
        "linkedin": "https://linkedin.com/in/james-vandenberg",
        "orcid": "0000-0002-3456-7890",
        "credentials": "MBChB, PhD, FRCPE, Professor of Medicine",
    },
    {
        "first_name": "Zanele",
        "last_name": "Dlamini",
        "email": "zanele.dlamini@example.com",
        "headline": "Digital Transformation & Enterprise Technology Leader",
        "bio": "Zanele Dlamini has led digital transformation initiatives for Fortune 500 companies and major South African enterprises. She specializes in cloud architecture, DevOps, and enterprise systems integration with a focus on African market requirements.",
        "affiliation": "Independent Consultant",
        "location": "Johannesburg, South Africa",
        "expertise": ["Technology", "Digital Transformation"],
        "years_experience": 14,
        "rate_60_min": 2800,
        "linkedin": "https://linkedin.com/in/zanele-dlamini",
        "orcid": "",
        "credentials": "AWS Solutions Architect, Microsoft Azure Expert, TOGAF Certified",
    },
    {
        "first_name": "Dr. Pieter",
        "last_name": "Botha",
        "email": "pieter.botha@example.com",
        "headline": "Mining & Energy Sector Specialist | PhD Geology",
        "bio": "Dr. Pieter Botha brings 18 years of experience in the mining and energy sectors. He has advised on major mining projects across Africa and specializes in geological assessments, resource valuation, and sustainable mining practices.",
        "affiliation": "Botha Geological Services",
        "location": "Johannesburg, South Africa",
        "expertise": ["Mining", "Energy"],
        "years_experience": 18,
        "rate_60_min": 3200,
        "linkedin": "https://linkedin.com/in/pieter-botha",
        "orcid": "0000-0003-4567-8901",
        "credentials": "PhD Geology (Wits), Pr.Sci.Nat, SACNASP Registered",
    },
    {
        "first_name": "Ayanda",
        "last_name": "Ngcobo",
        "email": "ayanda.ngcobo@example.com",
        "headline": "Legal & Regulatory Compliance Expert | Admitted Attorney",
        "bio": "Ayanda Ngcobo is an admitted attorney specializing in corporate law, regulatory compliance, and BBBEE advisory. She has guided numerous companies through complex regulatory landscapes and transaction structuring in South Africa.",
        "affiliation": "Ngcobo Legal Consulting",
        "location": "Durban, South Africa",
        "expertise": ["Legal", "Compliance"],
        "years_experience": 11,
        "rate_60_min": 2600,
        "linkedin": "https://linkedin.com/in/ayanda-ngcobo",
        "orcid": "",
        "credentials": "LLB (UKZN), LLM Commercial Law, Admitted Attorney of the High Court",
    },
    {
        "first_name": "Dr. Fatima",
        "last_name": "Patel",
        "email": "fatima.patel@example.com",
        "headline": "Supply Chain & Operations Excellence Specialist",
        "bio": "Dr. Fatima Patel is an operations expert with deep experience in supply chain optimization, manufacturing excellence, and logistics. She has implemented lean manufacturing systems across multiple industries in Africa and the Middle East.",
        "affiliation": "Patel Operations Consulting",
        "location": "Cape Town, South Africa",
        "expertise": ["Operations", "Supply Chain"],
        "years_experience": 16,
        "rate_60_min": 2700,
        "linkedin": "https://linkedin.com/in/fatima-patel",
        "orcid": "",
        "credentials": "PhD Industrial Engineering (Stellenbosch), Six Sigma Black Belt, PMP",
    },
    {
        "first_name": "Sipho",
        "last_name": "Mthembu",
        "email": "sipho.mthembu@example.com",
        "headline": "Marketing Strategy & Brand Development Expert",
        "bio": "Sipho Mthembu is a marketing strategist who has built and launched brands across Africa. He specializes in market entry strategies, consumer research, and digital marketing for both startups and established enterprises.",
        "affiliation": "Mthembu Brand Partners",
        "location": "Johannesburg, South Africa",
        "expertise": ["Marketing", "Strategy"],
        "years_experience": 13,
        "rate_60_min": 2400,
        "linkedin": "https://linkedin.com/in/sipho-mthembu",
        "orcid": "",
        "credentials": "MBA Marketing (Gordon Institute), Google Digital Marketing Certified",
    },
    {
        "first_name": "Dr. Linda",
        "last_name": "Nkosi",
        "email": "linda.nkosi@example.com",
        "headline": "Human Capital & Organizational Development Expert",
        "bio": "Dr. Linda Nkosi is an organizational psychologist specializing in leadership development, talent management, and workplace culture transformation. She has worked with boards and executive teams across multiple industries.",
        "affiliation": "Nkosi People Advisory",
        "location": "Johannesburg, South Africa",
        "expertise": ["Human Resources", "Leadership"],
        "years_experience": 17,
        "rate_60_min": 2900,
        "linkedin": "https://linkedin.com/in/linda-nkosi",
        "orcid": "0000-0004-5678-9012",
        "credentials": "PhD Organizational Psychology (Wits), SABPP Master HR Practitioner",
    },
    {
        "first_name": "Prof. Ahmed",
        "last_name": "Moosa",
        "email": "ahmed.moosa@example.com",
        "headline": "Renewable Energy & Sustainability Expert",
        "bio": "Professor Ahmed Moosa is a leading voice in renewable energy and sustainability in Africa. He advises governments and corporations on clean energy transitions, carbon strategies, and sustainable development with a focus on African contexts.",
        "affiliation": "University of Cape Town",
        "location": "Cape Town, South Africa",
        "expertise": ["Energy", "Sustainability"],
        "years_experience": 19,
        "rate_60_min": 3100,
        "linkedin": "https://linkedin.com/in/ahmed-moosa",
        "orcid": "0000-0005-6789-0123",
        "credentials": "PhD Energy Studies (UCT), Chartered Environmentalist, IPCC Contributing Author",
    },
]


EXPERTISE_TAGS = [
    ("Artificial Intelligence", "discipline"),
    ("Data Science", "discipline"),
    ("Finance", "discipline"),
    ("Strategy", "discipline"),
    ("Healthcare", "discipline"),
    ("Research", "discipline"),
    ("Technology", "discipline"),
    ("Digital Transformation", "discipline"),
    ("Mining", "industry"),
    ("Energy", "industry"),
    ("Legal", "discipline"),
    ("Compliance", "discipline"),
    ("Operations", "discipline"),
    ("Supply Chain", "discipline"),
    ("Marketing", "discipline"),
    ("Human Resources", "discipline"),
    ("Leadership", "discipline"),
    ("Sustainability", "discipline"),
]


class Command(BaseCommand):
    help = 'Seeds the database with 10 vetted dummy experts for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Creating expertise tags...')
        tags = {}
        for name, tag_type in EXPERTISE_TAGS:
            tag, created = ExpertiseTag.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'tag_type': tag_type}
            )
            tags[name] = tag
            if created:
                self.stdout.write(f'  Created tag: {name}')
        
        self.stdout.write('\nCreating dummy experts...')
        for expert_data in DUMMY_EXPERTS:
            user, created = User.objects.get_or_create(
                email=expert_data['email'],
                defaults={
                    'first_name': expert_data['first_name'],
                    'last_name': expert_data['last_name'],
                    'role': 'expert',
                    'email_verified': True,
                    'terms_accepted': True,
                }
            )
            
            if created:
                user.set_password('demo123')
                user.save()
            
            profile, profile_created = ExpertProfile.objects.get_or_create(
                user=user,
                defaults={
                    'headline': expert_data['headline'],
                    'bio': expert_data['bio'],
                    'affiliation': expert_data['affiliation'],
                    'location': expert_data['location'],
                    'rate_60_min': expert_data['rate_60_min'],
                    'rate_30_min': int(expert_data['rate_60_min'] * 0.6),
                    'rate_90_min': int(expert_data['rate_60_min'] * 1.4),
                    'orcid_id': expert_data.get('orcid', ''),
                    'verification_status': 'verified',
                    'is_publicly_listed': True,
                    'average_rating': 4.5,
                    'total_reviews': 12,
                    'languages': ['English'],
                }
            )
            
            for exp_name in expert_data['expertise']:
                if exp_name in tags:
                    profile.expertise_tags.add(tags[exp_name])
            
            status = 'Created' if profile_created else 'Updated'
            self.stdout.write(f'  {status}: {expert_data["first_name"]} {expert_data["last_name"]}')
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully seeded 10 dummy experts!'))
        self.stdout.write('\nExpert documentation:')
        self.stdout.write('-' * 80)
        
        for expert_data in DUMMY_EXPERTS:
            self.stdout.write(f"\nName: {expert_data['first_name']} {expert_data['last_name']}")
            self.stdout.write(f"Field of Expertise: {', '.join(expert_data['expertise'])}")
            self.stdout.write(f"Years of Experience: {expert_data['years_experience']}")
            self.stdout.write(f"Credentials: {expert_data['credentials']}")
            self.stdout.write(f"LinkedIn: {expert_data['linkedin']}")
            self.stdout.write(f"Verification Status: Verified")
            self.stdout.write(f"Bio: {expert_data['bio'][:100]}...")
