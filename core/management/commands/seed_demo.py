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


class Command(BaseCommand):
    help = 'Seed demo users and test data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...\n')
        
        self.create_expertise_tags()
        self.create_admin_user()
        self.create_ops_user()
        self.create_client_user()
        self.create_expert_user()
        self.create_blog_posts()
        self.create_demo_requests_and_bookings()
        
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!\n'))
        self.stdout.write('\n=== Demo Account Credentials ===\n')
        self.stdout.write('Admin:  admin@kairos.africa / KairosAdmin123!\n')
        self.stdout.write('Ops:    ops@kairos.africa / KairosOps123!\n')
        self.stdout.write('Client: client@kairos.africa / KairosClient123!\n')
        self.stdout.write('Expert: expert@kairos.africa / KairosExpert123!\n')

    def create_expertise_tags(self):
        tags = [
            ('Fintech', 'fintech', 'discipline'),
            ('Banking', 'banking', 'industry'),
            ('Regulatory', 'regulatory', 'discipline'),
            ('Risk Management', 'risk-management', 'discipline'),
            ('Emerging Markets', 'emerging-markets', 'industry'),
            ('Private Equity', 'private-equity', 'industry'),
            ('Strategy', 'strategy', 'discipline'),
            ('Due Diligence', 'due-diligence', 'discipline'),
        ]
        
        for name, slug, tag_type in tags:
            ExpertiseTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'tag_type': tag_type}
            )
        
        self.stdout.write(self.style.SUCCESS('  Created expertise tags'))

    def create_admin_user(self):
        admin, created = User.objects.get_or_create(
            email='admin@kairos.africa',
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
            email='ops@kairos.africa',
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
            email='client@kairos.africa',
            defaults={
                'first_name': 'Morgan',
                'last_name': 'Naidoo',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
                'role': User.Role.CLIENT,
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

    def create_expert_user(self):
        expert_user, created = User.objects.get_or_create(
            email='expert@kairos.africa',
            defaults={
                'first_name': 'Naledi',
                'last_name': 'Mbeki',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
                'role': User.Role.EXPERT,
                'email_verified': True,
                'privacy_consent': True,
                'terms_accepted': True,
            }
        )
        
        if created:
            expert_user.set_password('KairosExpert123!')
            expert_user.save()
            self.stdout.write(self.style.SUCCESS('  Created expert user'))
        else:
            self.stdout.write('  Expert user already exists')
        
        profile, profile_created = ExpertProfile.objects.get_or_create(
            user=expert_user,
            defaults={
                'headline': 'Former fintech risk lead and emerging markets advisor',
                'bio': 'Over 18 years of experience in financial services across Africa. Former Chief Risk Officer at a leading pan-African bank, with deep expertise in regulatory compliance, fintech partnerships, and emerging market risk frameworks. Advised multiple private equity firms on due diligence for African financial services investments.',
                'affiliation': 'Independent Advisor',
                'location': 'Johannesburg, South Africa',
                'timezone': 'Africa/Johannesburg',
                'languages': ['English', 'Zulu', 'Afrikaans'],
                'years_experience': 18,
                'sector_expertise': 'Fintech, Banking, Regulatory, Risk Management',
                'privacy_level': ExpertProfile.PrivacyLevel.SEMI_PRIVATE,
                'verification_status': ExpertProfile.VerificationStatus.VETTED,
                'is_publicly_listed': True,
                'verification_submitted_at': timezone.now(),
                'verification_reviewed_at': timezone.now(),
            }
        )
        
        if profile_created:
            tags = ExpertiseTag.objects.filter(slug__in=['fintech', 'banking', 'regulatory', 'risk-management'])
            profile.expertise_tags.set(tags)
            self.stdout.write(self.style.SUCCESS('  Created expert profile'))
        else:
            self.stdout.write('  Expert profile already exists')

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
                'content': '''<p>Africa is home to some of the world's most innovative financial services markets, rapidly evolving regulatory frameworks, and business environments that demand exceptional adaptability. Yet when global organisations need African expertise, finding the right people remains surprisingly difficult.</p>

<h2>The expertise gap</h2>

<p>Consider this scenario: a European private equity firm is evaluating a fintech acquisition in West Africa. They need to understand local regulatory requirements, competitive dynamics, and operational risks. Where do they turn?</p>

<p>Traditional consulting firms can provide generic market reports. Local advisors may have relationships but limited sector depth. Former executives from relevant companies are difficult to identify and even harder to approach professionally.</p>

<p>This gap represents a significant inefficiency. Brilliant minds across the continent—former central bankers, industry pioneers, regulatory experts—possess invaluable knowledge. Yet connecting with them remains an exercise in networking luck rather than systematic access.</p>

<h2>Our approach</h2>

<p>Kairos was built in South Africa specifically to address this challenge. We are creating infrastructure that:</p>

<ul>
<li><strong>Surfaces hidden expertise:</strong> Identifying and vetting experts across African markets who have deep, relevant experience</li>
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
        client = User.objects.filter(email='client@kairos.africa').first()
        expert_profile = ExpertProfile.objects.filter(user__email='expert@kairos.africa').first()
        admin = User.objects.filter(email='admin@kairos.africa').first()
        
        if not client or not expert_profile:
            self.stdout.write(self.style.WARNING('  Skipping demo bookings: client or expert not found'))
            return

        fintech_tag = ExpertiseTag.objects.filter(slug='fintech').first()
        regulatory_tag = ExpertiseTag.objects.filter(slug='regulatory').first()

        request_1, created = ClientRequest.objects.get_or_create(
            email='client@kairos.africa',
            company='Umkhonto Capital',
            status=ClientRequest.Status.PENDING,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'We are evaluating a potential investment in a South African fintech company focused on cross-border payments. We need expert input on regulatory requirements across SADC markets, particularly regarding mobile money licensing and foreign exchange compliance.',
                'engagement_type': ClientRequest.EngagementType.CONSULTATION,
                'timeline_urgency': ClientRequest.UrgencyLevel.MEDIUM,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.ELEVATED,
            }
        )
        if created:
            if fintech_tag:
                request_1.preferred_expertise.add(fintech_tag)
            if regulatory_tag:
                request_1.preferred_expertise.add(regulatory_tag)
            self.stdout.write(self.style.SUCCESS('  Created pending client request'))
        else:
            self.stdout.write('  Pending client request already exists')

        request_2, created = ClientRequest.objects.get_or_create(
            email='client@kairos.africa',
            company='Umkhonto Capital',
            status=ClientRequest.Status.MATCHED,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'Need guidance on establishing a digital banking framework in Kenya. Looking for expertise on Central Bank of Kenya regulations and licensing requirements.',
                'engagement_type': ClientRequest.EngagementType.ADVISORY,
                'timeline_urgency': ClientRequest.UrgencyLevel.HIGH,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.STANDARD,
                'matched_expert': expert_profile,
                'matched_by': admin,
                'matched_at': timezone.now() - timedelta(days=3),
            }
        )
        if created:
            if regulatory_tag:
                request_2.preferred_expertise.add(regulatory_tag)
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
                'scope': 'Advisory session on digital banking licensing in Kenya',
                'duration_description': '1 hour consultation',
                'scheduled_start': timezone.now() + timedelta(days=2),
                'scheduled_end': timezone.now() + timedelta(days=2, hours=1),
                'problem_statement': 'Need guidance on establishing a digital banking framework in Kenya.',
                'amount': 500.00,
                'expert_payout': 400.00,
                'currency': 'GBP',
                'terms_accepted': True,
                'terms_accepted_at': timezone.now() - timedelta(days=2),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created scheduled booking'))
        else:
            self.stdout.write('  Scheduled booking already exists')

        request_3, created = ClientRequest.objects.get_or_create(
            email='client@kairos.africa',
            company='Umkhonto Capital',
            status=ClientRequest.Status.IN_PROGRESS,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'Ongoing advisory on risk management frameworks for African fintech expansion.',
                'engagement_type': ClientRequest.EngagementType.ADVISORY,
                'timeline_urgency': ClientRequest.UrgencyLevel.LOW,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.STRICT,
                'matched_expert': expert_profile,
                'matched_by': admin,
                'matched_at': timezone.now() - timedelta(days=14),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created in-progress client request'))

        booking_ongoing, created = Booking.objects.get_or_create(
            client=client,
            expert=expert_profile,
            status=Booking.Status.IN_SESSION,
            defaults={
                'client_request': request_3,
                'service_type': Booking.ServiceType.ADVISORY,
                'scope': 'Multi-week advisory engagement on risk frameworks',
                'duration_description': '4 weeks ongoing advisory',
                'scheduled_start': timezone.now() - timedelta(days=7),
                'problem_statement': 'Ongoing advisory on risk management frameworks for African fintech expansion.',
                'amount': 2500.00,
                'expert_payout': 2000.00,
                'currency': 'GBP',
                'terms_accepted': True,
                'terms_accepted_at': timezone.now() - timedelta(days=14),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created ongoing booking'))
        else:
            self.stdout.write('  Ongoing booking already exists')

        request_4, created = ClientRequest.objects.get_or_create(
            email='client@kairos.africa',
            company='Umkhonto Capital',
            status=ClientRequest.Status.COMPLETED,
            defaults={
                'name': 'Morgan Naidoo',
                'client': client,
                'problem_description': 'Due diligence support for a proposed acquisition of a Nigerian payments company.',
                'engagement_type': ClientRequest.EngagementType.RESEARCH,
                'timeline_urgency': ClientRequest.UrgencyLevel.HIGH,
                'confidentiality_level': ClientRequest.ConfidentialityLevel.STRICT,
                'matched_expert': expert_profile,
                'matched_by': admin,
                'matched_at': timezone.now() - timedelta(days=45),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created completed client request'))

        booking_completed, created = Booking.objects.get_or_create(
            client=client,
            expert=expert_profile,
            status=Booking.Status.COMPLETED,
            defaults={
                'client_request': request_4,
                'service_type': Booking.ServiceType.RESEARCH,
                'scope': 'Full due diligence on Nigerian payments company acquisition',
                'duration_description': '3 weeks research engagement',
                'scheduled_start': timezone.now() - timedelta(days=40),
                'scheduled_end': timezone.now() - timedelta(days=25),
                'problem_statement': 'Due diligence support for a proposed acquisition of a Nigerian payments company.',
                'amount': 5000.00,
                'expert_payout': 4000.00,
                'currency': 'GBP',
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
                    'comment': 'Exceptional expertise and professionalism. Naledi provided invaluable insights into the Nigerian payments landscape that directly informed our investment decision. Highly recommended.',
                    'is_public': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('  Created review on completed booking'))
            else:
                self.stdout.write('  Review already exists')
