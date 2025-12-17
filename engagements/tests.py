"""
Tests for engagements app.
"""
from django.test import TestCase, Client

from accounts.models import User
from engagements.models import ClientRequest, ExpertMatch, Engagement
from engagements.enums import ClientRequestStatus, ExpertMatchStatus, EngagementStatus


class VerifiedClientGateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.pending_client = User.objects.create_user(
            email='pending@test.com',
            password='testpass123',
            first_name='Pending',
            last_name='Client',
            role=User.Role.CLIENT,
            client_status=User.ClientStatus.PENDING,
        )
        self.verified_client = User.objects.create_user(
            email='verified@test.com',
            password='testpass123',
            first_name='Verified',
            last_name='Client',
            role=User.Role.CLIENT,
            client_status=User.ClientStatus.VERIFIED,
        )
        self.expert_user = User.objects.create_user(
            email='expert@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Expert',
            role=User.Role.EXPERT,
            expert_status=User.ExpertStatusChoices.ACTIVE,
        )

    def test_pending_client_cannot_access_expert_shortlist(self):
        self.client.login(email='pending@test.com', password='testpass123')
        request = ClientRequest.objects.create(
            client=self.pending_client,
            organisation_name='Test Org',
            brief='Test brief',
            status=ClientRequestStatus.SHORTLISTED,
        )
        self.assertFalse(request.can_view_experts(self.pending_client))

    def test_verified_client_can_access_expert_shortlist(self):
        self.client.login(email='verified@test.com', password='testpass123')
        request = ClientRequest.objects.create(
            client=self.verified_client,
            organisation_name='Test Org',
            brief='Test brief',
            status=ClientRequestStatus.SHORTLISTED,
        )
        self.assertTrue(request.can_view_experts(self.verified_client))

    def test_verified_client_cannot_view_experts_before_shortlist(self):
        request = ClientRequest.objects.create(
            client=self.verified_client,
            organisation_name='Test Org',
            brief='Test brief',
            status=ClientRequestStatus.SUBMITTED,
        )
        self.assertFalse(request.can_view_experts(self.verified_client))


class ClientRequestModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Client',
            role=User.Role.CLIENT,
            client_status=User.ClientStatus.VERIFIED,
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Admin',
            role=User.Role.ADMIN,
        )

    def test_create_client_request(self):
        request = ClientRequest.objects.create(
            client=self.client_user,
            organisation_name='Test Company',
            brief='We need help with machine learning',
        )
        self.assertEqual(request.status, ClientRequestStatus.SUBMITTED)
        self.assertEqual(str(request), 'Request from Test Company - Submitted')

    def test_advance_creates_progress_event(self):
        request = ClientRequest.objects.create(
            client=self.client_user,
            organisation_name='Test Company',
            brief='Test brief',
        )
        request.status = ClientRequestStatus.IN_REVIEW
        request.advance('request_in_review', actor=self.admin_user)
        self.assertEqual(request.progress_events.count(), 1)


class ExpertMatchModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Client',
            role=User.Role.CLIENT,
            client_status=User.ClientStatus.VERIFIED,
        )
        self.expert_user = User.objects.create_user(
            email='expert@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Expert',
            role=User.Role.EXPERT,
            expert_status=User.ExpertStatusChoices.ACTIVE,
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Admin',
            role=User.Role.ADMIN,
        )
        self.request = ClientRequest.objects.create(
            client=self.client_user,
            organisation_name='Test Company',
            brief='Test brief',
        )

    def test_create_expert_match(self):
        match = ExpertMatch.objects.create(
            request=self.request,
            expert=self.expert_user,
            proposed_by=self.admin_user,
        )
        self.assertEqual(match.status, ExpertMatchStatus.PROPOSED)

    def test_accept_expert_match(self):
        match = ExpertMatch.objects.create(
            request=self.request,
            expert=self.expert_user,
            proposed_by=self.admin_user,
        )
        match.status = ExpertMatchStatus.ACCEPTED
        match.save()
        self.assertEqual(match.status, ExpertMatchStatus.ACCEPTED)


class EngagementModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Client',
            role=User.Role.CLIENT,
            client_status=User.ClientStatus.VERIFIED,
        )
        self.expert_user = User.objects.create_user(
            email='expert@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Expert',
            role=User.Role.EXPERT,
            expert_status=User.ExpertStatusChoices.ACTIVE,
        )
        self.request = ClientRequest.objects.create(
            client=self.client_user,
            organisation_name='Test Company',
            brief='Test brief',
        )

    def test_create_engagement(self):
        engagement = Engagement.objects.create(
            request=self.request,
            expert=self.expert_user,
        )
        self.assertEqual(engagement.status, EngagementStatus.SCHEDULED)

    def test_advance_engagement_creates_progress_event(self):
        engagement = Engagement.objects.create(
            request=self.request,
            expert=self.expert_user,
        )
        engagement.advance(EngagementStatus.IN_PROGRESS)
        self.assertEqual(engagement.status, EngagementStatus.IN_PROGRESS)
        self.assertEqual(self.request.progress_events.count(), 1)
