"""
Management command to seed demo data for testing.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from experts.models import ExpertProfile, ExpertiseTag
from consultations.models import ClientRequest, Booking, Review
from blog.models import BlogPost
from engagements.models import (
    ClientRequest as EngagementRequest,
    ExpertMatch,
    Engagement,
    ProgressEvent,
)
from engagements.enums import (
    ClientRequestStatus,
    ExpertMatchStatus,
    EngagementStatus,
    ProgressEventType,
)


class Command(BaseCommand):
    help = 'Seed demo users and test data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...\n')
        
        self.create_expertise_tags()
        self.create_admin_user()
        self.create_ops_user()
        self.create_client_user()
        self.create_diverse_experts()
        self.create_blog_posts()
        self.create_demo_requests_and_bookings()
        self.create_engagement_workflow_data()
        
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!\n'))
        self.stdout.write('\n=== Demo account credentials ===\n')
        self.stdout.write('Admin:  admin@kairos.co.za / KairosAdmin123!\n')
        self.stdout.write('Ops:    ops@kairos.co.za / KairosOps123!\n')
        self.stdout.write('Client: client@kairos.co.za / KairosClient123!\n')
        self.stdout.write('Expert: dr.molefe@kairos.co.za / KairosExpert123!\n')

    def create_expertise_tags(self):
        tags = [
            ('Computational biology', 'computational-biology', 'discipline'),
            ('Machine learning', 'machine-learning', 'discipline'),
            ('Materials science', 'materials-science', 'discipline'),
            ('Quantitative finance', 'quantitative-finance', 'discipline'),
            ('Clinical research', 'clinical-research', 'discipline'),
            ('Regulatory affairs', 'regulatory-affairs', 'discipline'),
            ('Risk modelling', 'risk-modelling', 'discipline'),
            ('Policy analysis', 'policy-analysis', 'discipline'),
            ('Technical due diligence', 'technical-due-diligence', 'discipline'),
            ('Fintech', 'fintech', 'industry'),
            ('Healthcare', 'healthcare', 'industry'),
            ('Energy', 'energy', 'industry'),
            ('Mining', 'mining', 'industry'),
            ('Banking', 'banking', 'industry'),
            ('Private equity', 'private-equity', 'industry'),
            ('STEM', 'stem', 'discipline'),
        ]
        
        for name, slug, tag_type in tags:
            ExpertiseTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'tag_type': tag_type}
            )
        
        self.stdout.write(self.style.SUCCESS('  Created expertise tags'))

    def create_admin_user(self):
        admin, created = User.objects.get_or_create(
            email='admin@kairos.co.za',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Kairos',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': User.Role.ADMIN,
                'email_verified': True,
                'privacy_consent': True,
                'terms_accepted': True,
            }
        )
        
        if created:
            admin.set_password('KairosAdmin123!')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  Created admin user'))
        else:
            self.stdout.write('  Admin user already exists')

    def create_ops_user(self):
        ops, created = User.objects.get_or_create(
            email='ops@kairos.co.za',
            defaults={
                'first_name': 'Operations',
                'last_name': 'Manager',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
                'role': User.Role.ADMIN,
                'email_verified': True,
                'privacy_consent': True,
                'terms_accepted': True,
            }
        )
        
        if created:
            ops.set_password('KairosOps123!')
            ops.save()
            self.stdout.write(self.style.SUCCESS('  Created operations user'))
        else:
            self.stdout.write('  Operations user already exists')

    def create_client_user(self):
        client, created = User.objects.get_or_create(
            email='client@kairos.co.za',
            defaults={
                'first_name': 'Morgan',
                'last_name': 'Naidoo',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
                'role': User.Role.CLIENT,
                'client_status': User.ClientStatus.VERIFIED,
                'email_verified': True,
                'privacy_consent': True,
                'terms_accepted': True,
            }
        )
        
        if created:
            client.set_password('KairosClient123!')
            client.save()
            self.stdout.write(self.style.SUCCESS('  Created client user'))
        else:
            self.stdout.write('  Client user already exists')

    def create_diverse_experts(self):
        experts_data = [
            {
                'email': 'dr.molefe@kairos.co.za',
                'first_name': 'Thabo',
                'last_name': 'Molefe',
                'headline': 'Computational biology specialist | Machine learning for drug discovery',
                'bio': 'PhD in Computational Biology from the University of Cape Town. Research focus on applying machine learning methods to genomic data analysis and drug target identification. Published in Nature Communications and PLOS Computational Biology. Advisory experience includes technical due diligence for biotech investments and clinical study design consultation.',
                'affiliation': 'University of Cape Town (affiliated)',
                'location': 'Cape Town, South Africa',
                'sector_expertise': 'Computational biology, Machine learning, Drug discovery, Genomics',
                'tags': ['computational-biology', 'machine-learning', 'clinical-research', 'technical-due-diligence'],
                'privacy_level': ExpertProfile.PrivacyLevel.SEMI_PRIVATE,
                'years_experience': 12,
                'average_rating': 4.8,
            },
            {
                'email': 'prof.dlamini@kairos.co.za',
                'first_name': 'Nomvula',
                'last_name': 'Dlamini',
                'headline': 'Professor emeritus | Regulatory policy and financial systems',
                'bio': 'Former Professor of Economics at the University of the Witwatersrand. Served as an advisor to the South African Reserve Bank and National Treasury. Specialises in financial regulation, monetary policy, and emerging market dynamics. Extensive board experience with major financial institutions. Currently provides strategic advisory to private equity firms on regulatory risk assessment.',
                'affiliation': 'Independent advisor (formerly Wits University)',
                'location': 'Johannesburg, South Africa',
                'sector_expertise': 'Financial regulation, Monetary policy, Central banking, Risk assessment',
                'tags': ['regulatory-affairs', 'policy-analysis', 'banking', 'private-equity'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 35,
                'average_rating': 4.9,
            },
            {
                'email': 'dr.okonkwo@kairos.co.za',
                'first_name': 'Adaeze',
                'last_name': 'Okonkwo',
                'headline': 'Early-career PhD | Materials science and renewable energy systems',
                'bio': 'Recently completed PhD in Materials Science from Stellenbosch University with distinction. Research focus on advanced battery materials and solar cell efficiency. Published in Advanced Energy Materials and Journal of Materials Chemistry. Niche expertise in perovskite solar cells and solid-state battery technology. Available for technical review and R&D consultation.',
                'affiliation': 'Stellenbosch University (postdoctoral)',
                'location': 'Stellenbosch, South Africa',
                'sector_expertise': 'Materials science, Battery technology, Solar energy, R&D',
                'tags': ['materials-science', 'stem', 'energy', 'technical-due-diligence'],
                'privacy_level': ExpertProfile.PrivacyLevel.SEMI_PRIVATE,
                'years_experience': 6,
                'average_rating': 4.7,
            },
            {
                'email': 'dr.vanwyk@kairos.co.za',
                'first_name': 'Johan',
                'last_name': 'van Wyk',
                'headline': 'Quantitative finance specialist | Risk model development',
                'bio': 'PhD in Applied Mathematics from the University of Pretoria. Former Head of Quantitative Research at a leading South African asset manager. Expertise in derivatives pricing, risk model validation, and algorithmic trading systems. Advisory experience includes model validation for regulatory submissions and technical due diligence on fintech acquisitions.',
                'affiliation': 'Independent consultant',
                'location': 'Pretoria, South Africa',
                'sector_expertise': 'Quantitative finance, Risk modelling, Derivatives, Fintech',
                'tags': ['quantitative-finance', 'risk-modelling', 'fintech', 'technical-due-diligence'],
                'privacy_level': ExpertProfile.PrivacyLevel.SEMI_PRIVATE,
                'years_experience': 18,
                'average_rating': 4.6,
            },
            {
                'email': 'dr.nthakane@kairos.co.za',
                'first_name': 'Lesedi',
                'last_name': 'Nthakane',
                'headline': 'NLP and language technology researcher | Text analytics and AI',
                'bio': 'PhD in Computational Linguistics from University of the Witwatersrand. Specializes in natural language processing, sentiment analysis, and multilingual AI systems. Published extensively in ACL and EMNLP. Advisory on AI implementation and responsible AI governance. Expertise in African language NLP.',
                'affiliation': 'Research consultant (formerly Wits University)',
                'location': 'Johannesburg, South Africa',
                'sector_expertise': 'NLP, AI, Text analytics, Language technology',
                'tags': ['machine-learning', 'stem', 'technical-due-diligence'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 10,
                'average_rating': 4.7,
            },
            {
                'email': 'prof.masondo@kairos.co.za',
                'first_name': 'Dr. Mandla',
                'last_name': 'Masondo',
                'headline': 'Public health epidemiologist | Disease modelling and health systems',
                'bio': 'Retired Professor of Public Health from the University of KwaZulu-Natal with 40+ years experience. Previously headed epidemiology department. Expert in disease surveillance, health systems strengthening, and pandemic preparedness. Advisor to WHO and national health ministries. Focus on African health challenges.',
                'affiliation': 'Consulting professor (formerly UKZN)',
                'location': 'Durban, South Africa',
                'sector_expertise': 'Public health, Epidemiology, Health systems, Disease modelling',
                'tags': ['clinical-research', 'policy-analysis', 'healthcare'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 42,
                'average_rating': 4.9,
            },
            {
                'email': 'ms.venter@kairos.co.za',
                'first_name': 'Renée',
                'last_name': 'Venter',
                'headline': 'Fintech and blockchain strategist | Digital financial inclusion',
                'bio': 'Former VP of Strategic Partnerships at major fintech startup. 15+ years in financial services innovation and digital payments. Expert in blockchain regulation, payment systems, and financial inclusion in emerging markets. Board advisor to multiple fintech ventures.',
                'affiliation': 'Independent strategic advisor',
                'location': 'Cape Town, South Africa',
                'sector_expertise': 'Fintech, Blockchain, Digital payments, Financial systems',
                'tags': ['fintech', 'regulatory-affairs', 'policy-analysis', 'banking'],
                'privacy_level': ExpertProfile.PrivacyLevel.SEMI_PRIVATE,
                'years_experience': 15,
                'average_rating': 4.8,
            },
            {
                'email': 'dr.chiang@kairos.co.za',
                'first_name': 'Dr. Wei',
                'last_name': 'Chiang',
                'headline': 'Mining engineer | Resource extraction and sustainability',
                'bio': 'PhD in Mining Engineering from University of Witwatersrand. 20+ years experience in precious metals, rare earths, and coal mining operations. Expert in environmental management, operational efficiency, and mine development in African context. Advisor on ESG compliance in extractive industries.',
                'affiliation': 'Independent consultant',
                'location': 'Johannesburg, South Africa',
                'sector_expertise': 'Mining, Resource extraction, Operations, Environmental management',
                'tags': ['mining', 'energy', 'technical-due-diligence', 'stem'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 20,
                'average_rating': 4.7,
            },
            {
                'email': 'ms.abdi@kairos.co.za',
                'first_name': 'Amina',
                'last_name': 'Abdi',
                'headline': 'Supply chain and operations strategist | Logistics in emerging markets',
                'bio': 'Former VP of Operations for major African logistics company. 18 years optimizing supply chains across sub-Saharan Africa. Expertise in last-mile delivery, cold chain management, and logistics networks. Advisor on operational excellence and efficiency.',
                'affiliation': 'Operations consulting',
                'location': 'Nairobi, Kenya (serves Africa)',
                'sector_expertise': 'Supply chain, Logistics, Operations, Distribution networks',
                'tags': ['technical-due-diligence', 'policy-analysis'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 18,
                'average_rating': 4.6,
            },
            {
                'email': 'dr.khumalo@kairos.co.za',
                'first_name': 'Dr. Sizwe',
                'last_name': 'Khumalo',
                'headline': 'Cybersecurity and information security expert | Enterprise security',
                'bio': 'PhD in Computer Science (cybersecurity focus). 12+ years as Chief Information Security Officer at Fortune 500 African operations. Expert in threat intelligence, compliance frameworks (POPIA, GDPR), and enterprise security architecture. Advisor to boards on cyber risk.',
                'affiliation': 'Independent CISO advisor',
                'location': 'Johannesburg, South Africa',
                'sector_expertise': 'Cybersecurity, Information security, Data protection, Compliance',
                'tags': ['stem', 'technical-due-diligence', 'regulatory-affairs'],
                'privacy_level': ExpertProfile.PrivacyLevel.PUBLIC,
                'years_experience': 12,
                'average_rating': 4.8,
            },
        ]
        
        for expert_data in experts_data:
            expert_user, created = User.objects.get_or_create(
                email=expert_data['email'],
                defaults={
                    'first_name': expert_data['first_name'],
                    'last_name': expert_data['last_name'],
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'role': User.Role.EXPERT,
                    'expert_status': User.ExpertStatusChoices.ACTIVE,
                    'email_verified': True,
                    'privacy_consent': True,
                    'terms_accepted': True,
                }
            )
            
            if created:
                expert_user.set_password('KairosExpert123!')
                expert_user.save()
                self.stdout.write(self.style.SUCCESS(f'  Created expert user: {expert_data["first_name"]} {expert_data["last_name"]}'))
            else:
                self.stdout.write(f'  Expert user already exists: {expert_data["email"]}')
            
            profile, profile_created = ExpertProfile.objects.get_or_create(
                user=expert_user,
                defaults={
                    'headline': expert_data['headline'],
                    'bio': expert_data['bio'],
                    'affiliation': expert_data['affiliation'],
                    'location': expert_data['location'],
                    'timezone': 'Africa/Johannesburg',
                    'languages': ['English'],
                    'sector_expertise': expert_data['sector_expertise'],
                    'privacy_level': expert_data['privacy_level'],
                    'verification_status': ExpertProfile.VerificationStatus.ACTIVE,
                    'is_publicly_listed': True,
                    'years_experience': expert_data.get('years_experience', 0),
                    'average_rating': expert_data.get('average_rating', 4.5),
                    'total_reviews': max(1, int((expert_data.get('average_rating', 4.5) - 4) * 100)),
                    'verification_submitted_at': timezone.now(),
                    'verification_reviewed_at': timezone.now(),
                }
            )
            
            if profile_created:
                tags = ExpertiseTag.objects.filter(slug__in=expert_data['tags'])
                profile.expertise_tags.set(tags)
                self.stdout.write(self.style.SUCCESS(f'  Created expert profile: {expert_data["first_name"]}'))

    def create_blog_posts(self):
        posts_data = [
            {
                'title': 'Why confidential expertise matters',
                'slug': 'why-confidential-expertise-matters',
                'excerpt': 'In high-stakes decisions, the quality of your information sources can make or break outcomes. Here is why discretion and verified expertise are essential.',
                'content': '''<p>When organisations face critical decisions—whether evaluating an acquisition target, navigating regulatory complexity, or entering new markets—they need more than data. They need insight from people who have been there before.</p>

<h2>The challenge of finding real expertise</h2>

<p>The internet has democratised information, but it has also made it harder to distinguish genuine expertise from surface-level knowledge. LinkedIn profiles may list impressive titles, but they rarely reveal the depth of someone's actual experience or their track record in similar situations.</p>

<p>For sensitive matters, the challenge is even greater. You cannot simply post your question publicly and hope the right person responds. The nature of your enquiry—what you are investigating, which markets you are considering, what deals you are evaluating—is often confidential in itself.</p>

<h2>Why verification matters</h2>

<p>At Kairos, we believe that access to expertise must be earned, not assumed. Every expert in our network has been carefully vetted:</p>

<ul>
<li>Credentials verified against original sources</li>
<li>Experience validated through reference checks</li>
<li>Track record assessed for relevance and depth</li>
<li>Communication skills evaluated for clarity and professionalism</li>
</ul>

<p>This rigorous process means that when you engage with a Kairos expert, you know you are speaking with someone who genuinely has the knowledge you need.</p>

<h2>Confidentiality as a foundation</h2>

<p>We treat every enquiry as sensitive by default. Your questions, your research focus, and your strategic interests remain private. We do not publish pricing, we do not broadcast who is seeking what expertise, and we never share client information without explicit consent.</p>

<p>This approach reflects our understanding that in business, timing and discretion often matter as much as the information itself.</p>''',
                'reading_time_minutes': 4,
            },
            {
                'title': 'The Kairos philosophy',
                'slug': 'the-kairos-philosophy',
                'excerpt': 'Understanding the meaning behind our name and the principles that guide how we connect decision-makers with expertise.',
                'content': '''<p>In ancient Greek, there were two words for time. <em>Chronos</em> referred to sequential, quantitative time—the steady ticking of a clock, the progression of hours and days. <em>Kairos</em>, by contrast, meant something quite different: the right moment, the opportune time, the decisive instant when action must be taken.</p>

<h2>Why timing matters</h2>

<p>In business, we are often slaves to chronos. Quarterly reports, annual budgets, project timelines—these sequential markers shape how we think about progress. But the most important decisions rarely conform to neat schedules.</p>

<p>A competitor makes an unexpected move. A regulatory landscape shifts. An acquisition target suddenly becomes available. In these moments, having access to the right expertise immediately can mean the difference between seizing an opportunity and watching it pass.</p>

<h2>Clarity at the decisive moment</h2>

<p>Our name reflects our core purpose: to ensure that when you face a critical decision, you have access to the clarity you need. Not next quarter. Not when it is convenient. But now—in the kairos moment when insight actually matters.</p>

<h2>How this shapes our approach</h2>

<p>This philosophy influences everything we do:</p>

<ul>
<li><strong>Speed without compromise:</strong> We maintain a ready network of verified experts so matching can happen quickly without sacrificing quality</li>
<li><strong>Concierge-led service:</strong> Our team actively manages the matching process, understanding your needs and presenting appropriate experts—not leaving you to scroll through profiles</li>
<li><strong>Flexible engagement:</strong> From a single consultation to ongoing advisory relationships, we adapt to what the situation requires</li>
</ul>

<p>In a world saturated with information, we believe the real scarcity is access to genuine expertise at the moment it is needed most. That is the gap Kairos exists to fill.</p>''',
                'reading_time_minutes': 3,
            },
            {
                'title': 'Building a trusted expert network in Africa',
                'slug': 'building-trusted-expert-network-africa',
                'excerpt': 'The African continent holds remarkable expertise that remains underutilised. Here is how Kairos is working to change that.',
                'content': '''<p>Africa produces exceptional technical and scientific talent. The continent's universities and research institutions develop world-class specialists in fields from computational biology to advanced materials science, regulatory frameworks to quantitative finance.</p>

<h2>The expertise gap</h2>

<p>Consider this scenario: a European private equity firm is evaluating a fintech acquisition in West Africa. They need to understand local regulatory requirements, competitive dynamics, and operational risks. Where do they turn?</p>

<p>Traditional consulting firms can provide generic market reports. Local advisors may have relationships but limited sector depth. Former executives from relevant companies are difficult to identify and even harder to approach professionally.</p>

<p>This gap represents a significant inefficiency. PhD researchers, distinguished academics, and domain specialists possess invaluable knowledge. Yet connecting with them remains an exercise in networking luck rather than systematic access.</p>

<h2>Our approach</h2>

<p>Kairos was built in South Africa specifically to address this challenge. We are creating infrastructure that:</p>

<ul>
<li><strong>Surfaces hidden expertise:</strong> Identifying and vetting specialists across African markets who have deep, relevant experience</li>
<li><strong>Enables professional engagement:</strong> Providing a platform where organisations can access this expertise through structured, confidential consultations</li>
<li><strong>Maintains quality standards:</strong> Applying rigorous verification to ensure every expert can deliver genuine value</li>
</ul>

<h2>Beyond borders</h2>

<p>While our roots are in South Africa, our vision is broader. We are building a network that connects African expertise with global demand—and simultaneously brings world-class international expertise to organisations operating on the continent.</p>

<p>The goal is not to be an African platform, but a globally credible expert network that happens to have exceptional depth in African markets. Based in South Africa, serving organisations globally.</p>

<p>As we grow, we remain committed to the principle that expertise should be accessible to those who need it, regardless of geography or existing relationships. The knowledge exists. We are simply building better ways to access it.</p>''',
                'reading_time_minutes': 4,
            },
        ]
        
        for post_data in posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    'title': post_data['title'],
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'reading_time_minutes': post_data['reading_time_minutes'],
                    'author_name': 'Kairos Team',
                    'is_published': True,
                    'published_at': timezone.now(),
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created blog post: {post.title}'))
            else:
                self.stdout.write(f'  Blog post already exists: {post.title}')

    def create_demo_requests_and_bookings(self):
        client = User.objects.filter(email='client@kairos.co.za').first()
        expert_profile = ExpertProfile.objects.filter(user__email='dr.molefe@kairos.co.za').first()
        admin = User.objects.filter(email='admin@kairos.co.za').first()
        
        if not client or not expert_profile:
            self.stdout.write(self.style.WARNING('  Skipping demo bookings: client or expert not found'))
            return

        comp_bio_tag = ExpertiseTag.objects.filter(slug='computational-biology').first()
        tech_dd_tag = ExpertiseTag.objects.filter(slug='technical-due-diligence').first()

        request_1, created = ClientRequest.objects.get_or_create(
            email='client@kairos.co.za',
            company='Umkhonto Capital',
            status=ClientRequest.Status.PENDING,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'We are evaluating a potential investment in a South African biotech company developing novel drug discovery platforms. We need expert input on the technical validity of their machine learning approach and assessment of their computational biology capabilities.',
                'engagement_type': ClientRequest.EngagementType.CONSULTATION,
                'timeline_urgency': ClientRequest.UrgencyLevel.MEDIUM,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.ELEVATED,
                'billing_email': 'accounts@umkhontocapital.co.za',
                'organisation_name': 'Umkhonto Capital (Pty) Ltd',
                'invoice_status': 'draft',
            }
        )
        if created:
            if comp_bio_tag:
                request_1.preferred_expertise.add(comp_bio_tag)
            if tech_dd_tag:
                request_1.preferred_expertise.add(tech_dd_tag)
            self.stdout.write(self.style.SUCCESS('  Created pending client request'))
        else:
            self.stdout.write('  Pending client request already exists')

        request_2, created = ClientRequest.objects.get_or_create(
            email='client@kairos.co.za',
            company='Umkhonto Capital',
            status=ClientRequest.Status.MATCHED,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'Technical due diligence on genomic data analysis methodology for a clinical research company acquisition.',
                'engagement_type': ClientRequest.EngagementType.ADVISORY,
                'timeline_urgency': ClientRequest.UrgencyLevel.HIGH,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.STRICT,
                'matched_expert': expert_profile,
                'matched_by': admin,
                'matched_at': timezone.now() - timedelta(days=3),
                'billing_email': 'accounts@umkhontocapital.co.za',
                'organisation_name': 'Umkhonto Capital (Pty) Ltd',
                'po_number': 'PO-2024-0892',
                'invoice_status': 'sent',
            }
        )
        if created:
            if comp_bio_tag:
                request_2.preferred_expertise.add(comp_bio_tag)
            self.stdout.write(self.style.SUCCESS('  Created matched client request'))
        else:
            self.stdout.write('  Matched client request already exists')

        booking_scheduled, created = Booking.objects.get_or_create(
            client=client,
            expert=expert_profile,
            status=Booking.Status.SCHEDULED,
            defaults={
                'client_request': request_2,
                'service_type': Booking.ServiceType.ADVISORY,
                'scope': 'Technical review of genomic analysis methodology',
                'duration_description': '2 hour consultation',
                'scheduled_start': timezone.now() + timedelta(days=2),
                'scheduled_end': timezone.now() + timedelta(days=2, hours=2),
                'problem_statement': 'Technical due diligence on genomic data analysis methodology.',
                'amount': 8500.00,
                'expert_payout': 6800.00,
                'currency': 'ZAR',
                'terms_accepted': True,
                'terms_accepted_at': timezone.now() - timedelta(days=2),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created scheduled booking'))
        else:
            self.stdout.write('  Scheduled booking already exists')

        request_3, created = ClientRequest.objects.get_or_create(
            email='client@kairos.co.za',
            company='Umkhonto Capital',
            status=ClientRequest.Status.COMPLETED,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'Clinical study design review for a pharmaceutical R&D investment opportunity.',
                'engagement_type': ClientRequest.EngagementType.RESEARCH,
                'timeline_urgency': ClientRequest.UrgencyLevel.HIGH,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.STRICT,
                'matched_expert': expert_profile,
                'matched_by': admin,
                'matched_at': timezone.now() - timedelta(days=45),
                'billing_email': 'accounts@umkhontocapital.co.za',
                'organisation_name': 'Umkhonto Capital (Pty) Ltd',
                'po_number': 'PO-2024-0756',
                'invoice_status': 'paid',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created completed client request'))

        booking_completed, created = Booking.objects.get_or_create(
            client=client,
            expert=expert_profile,
            status=Booking.Status.COMPLETED,
            defaults={
                'client_request': request_3,
                'service_type': Booking.ServiceType.RESEARCH,
                'scope': 'Clinical study design review and technical assessment',
                'duration_description': '3 weeks research engagement',
                'scheduled_start': timezone.now() - timedelta(days=40),
                'scheduled_end': timezone.now() - timedelta(days=25),
                'problem_statement': 'Clinical study design review for a pharmaceutical R&D investment opportunity.',
                'amount': 45000.00,
                'expert_payout': 36000.00,
                'currency': 'ZAR',
                'terms_accepted': True,
                'terms_accepted_at': timezone.now() - timedelta(days=42),
                'completed_at': timezone.now() - timedelta(days=25),
                'completed_by_expert': True,
                'completed_by_client': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created completed booking'))
        else:
            self.stdout.write('  Completed booking already exists')

        if booking_completed:
            review, created = Review.objects.get_or_create(
                booking=booking_completed,
                defaults={
                    'reviewer': client,
                    'reviewee': expert_profile.user,
                    'rating': 5,
                    'comment': 'Dr Molefe provided exceptional technical insight into the clinical study design. His expertise in computational biology was invaluable for our due diligence process. Highly recommended for complex biotech assessments.',
                    'is_public': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('  Created review for completed booking'))

    def create_engagement_workflow_data(self):
        client = User.objects.filter(email='client@kairos.co.za').first()
        admin = User.objects.filter(email='admin@kairos.co.za').first()
        expert_molefe = User.objects.filter(email='dr.molefe@kairos.co.za').first()
        expert_vanwyk = User.objects.filter(email='dr.vanwyk@kairos.co.za').first()

        if not all([client, admin, expert_molefe, expert_vanwyk]):
            self.stdout.write(self.style.WARNING('  Skipping engagement workflow data: required users not found'))
            return

        # Create or get the single demo request (stable identifier: client + specific brief start)
        demo_brief_start = 'We are evaluating an investment opportunity'
        
        eng_request = None
        try:
            eng_request = EngagementRequest.objects.get(
                client=client,
                brief__startswith=demo_brief_start,
                status=ClientRequestStatus.SUBMITTED,
            )
            self.stdout.write('  Engagement request (submitted) already exists')
        except EngagementRequest.DoesNotExist:
            eng_request = EngagementRequest.objects.create(
                client=client,
                organisation_name='Umkhonto Capital (Pty) Ltd',
                billing_email='accounts@umkhontocapital.co.za',
                phone='+27 11 555 0123',
                engagement_type='consultation',
                urgency='standard',
                brief='We are evaluating an investment opportunity in a South African biotechnology company developing AI-driven drug discovery platforms. We require expert input on the technical validity of their machine learning approach and an assessment of their computational biology capabilities.',
                confidentiality_level='restricted',
                status=ClientRequestStatus.SUBMITTED,
            )
            ProgressEvent.objects.create(
                request=eng_request,
                actor=client,
                event_type=ProgressEventType.REQUEST_SUBMITTED,
                message='Client submitted a new consultation request',
            )
            self.stdout.write(self.style.SUCCESS('  Created engagement request (submitted)'))

        # Create exactly two expert matches for the same request
        match_proposed, match_created = ExpertMatch.objects.get_or_create(
            request=eng_request,
            expert=expert_molefe,
            defaults={
                'proposed_by': admin,
                'status': ExpertMatchStatus.PROPOSED,
                'note_to_client': 'Dr Molefe has deep expertise in computational biology and ML-driven drug discovery.',
                'internal_note': 'Excellent match for technical assessment.',
            }
        )
        
        # If match already existed but status is wrong, update it to PROPOSED
        if not match_created and match_proposed.status != ExpertMatchStatus.PROPOSED:
            match_proposed.status = ExpertMatchStatus.PROPOSED
            match_proposed.save()
        
        if match_created:
            ProgressEvent.objects.create(
                request=eng_request,
                actor=admin,
                event_type=ProgressEventType.EXPERT_PROPOSED,
                message='Dr Molefe proposed as expert match',
            )
            self.stdout.write(self.style.SUCCESS('  Created expert match (proposed) - Dr Molefe'))
        else:
            self.stdout.write('  Expert match (proposed) - Dr Molefe already exists')

        match_declined, declined_created = ExpertMatch.objects.get_or_create(
            request=eng_request,
            expert=expert_vanwyk,
            defaults={
                'proposed_by': admin,
                'status': ExpertMatchStatus.DECLINED,
                'internal_note': 'Declined due to scheduling conflict.',
            }
        )
        
        # If match already existed but status is wrong, update it to DECLINED
        if not declined_created and match_declined.status != ExpertMatchStatus.DECLINED:
            match_declined.status = ExpertMatchStatus.DECLINED
            match_declined.save()
        
        if declined_created:
            self.stdout.write(self.style.SUCCESS('  Created expert match (declined) - Dr van Wyk'))
        else:
            self.stdout.write('  Expert match (declined) - Dr van Wyk already exists')

        # Create exactly one engagement linked to the proposed expert
        engagement, eng_created = Engagement.objects.get_or_create(
            request=eng_request,
            expert=expert_molefe,
            defaults={
                'status': EngagementStatus.SCHEDULED,
                'scheduled_start': timezone.now() + timedelta(days=5),
                'scheduled_end': timezone.now() + timedelta(days=5, hours=2),
                'meeting_mode': 'platform',
                'shared_notes': 'Pre-engagement: please review the attached company technical brief.',
            }
        )
        if eng_created:
            ProgressEvent.objects.create(
                request=eng_request,
                actor=admin,
                event_type=ProgressEventType.ENGAGEMENT_SCHEDULED,
                message='Engagement scheduled with Dr Molefe',
            )
            self.stdout.write(self.style.SUCCESS('  Created engagement (scheduled) with Dr Molefe'))
        else:
            self.stdout.write('  Engagement (scheduled) with Dr Molefe already exists')

        self.stdout.write(self.style.SUCCESS('\n  === Demo engagement workflow ==='))
        self.stdout.write(f'  Request ID: {eng_request.id}')
        self.stdout.write(f'  ClientRequest: 1 (status: {eng_request.get_status_display()})')
        
        expert_match_count = eng_request.expert_matches.count()
        self.stdout.write(f'  ExpertMatch: {expert_match_count}')
        for match in eng_request.expert_matches.all():
            self.stdout.write(f'    - {match.expert.full_name}: {match.get_status_display()}')
        
        engagement_count = eng_request.engagements.count()
        self.stdout.write(f'  Engagement: {engagement_count}')
        
        progress_event_count = eng_request.progress_events.count()
        self.stdout.write(f'  ProgressEvent: {progress_event_count}')
        for event in eng_request.progress_events.all():
            self.stdout.write(f'    - {event.get_event_type_display()}')
