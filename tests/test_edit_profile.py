from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from accounts.models import User
from experts.models import ExpertProfile
from experts.views import edit_profile

class EditProfileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='expert@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Expert',
            expert_status='active'
        )
        self.profile = ExpertProfile.objects.create(
            user=self.user,
            headline='Test Expert',
            bio='Test bio',
            verification_status='active'
        )

    def test_edit_profile_view_requires_login(self):
        """Unauthenticated users should be redirected to login"""
        client = Client()
        response = client.get(reverse('experts:edit_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_edit_profile_view_requires_expert_status(self):
        """Non-experts should be redirected to dashboard"""
        client = Client()
        non_expert = User.objects.create_user(
            email='client@test.com',
            password='TestPass123!'
        )
        client.force_login(non_expert)
        response = client.get(reverse('experts:edit_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    def test_edit_profile_expert_can_access(self):
        """Experts with ExpertProfile can access edit page"""
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse('experts:edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experts/edit_profile.html')
        self.assertIn('basic_form', response.context)
        self.assertIn('avatar_form', response.context)
        self.assertIn('expertise_form', response.context)
        self.assertIn('experience_form', response.context)

    def test_profile_fields_exist(self):
        """Test that new fields exist on ExpertProfile model"""
        self.assertTrue(hasattr(self.profile, 'cv_file'))
        self.assertTrue(hasattr(self.profile, 'linkedin_url'))
        self.assertTrue(hasattr(self.profile, 'github_url'))

    def test_form_includes_new_fields(self):
        """Test that forms include the new fields"""
        from experts.forms import ExpertProfileAvatarForm, ExpertProfileExpertiseForm
        
        avatar_form = ExpertProfileAvatarForm(instance=self.profile)
        expertise_form = ExpertProfileExpertiseForm(instance=self.profile)
        
        self.assertIn('cv_file', avatar_form.fields)
        self.assertIn('linkedin_url', expertise_form.fields)
        self.assertIn('github_url', expertise_form.fields)
