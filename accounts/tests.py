"""
Tests for accounts app.
"""
import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import User


@pytest.fixture
def test_user(db):
    """Create a test user for authentication tests."""
    user = User.objects.create_user(
        email='testuser@example.com',
        password='testpassword123',
        first_name='Test',
        last_name='User',
        privacy_consent=True,
        terms_accepted=True,
    )
    return user


@pytest.fixture
def authenticated_client(test_user):
    """Create an authenticated test client."""
    client = Client()
    client.login(email='testuser@example.com', password='testpassword123')
    return client


@pytest.mark.django_db
class TestLogout:
    """Tests for logout functionality."""

    def test_logout_redirects_to_home(self, authenticated_client):
        """Test that logout redirects to the home page."""
        response = authenticated_client.get(reverse('accounts:logout'))
        assert response.status_code == 302
        assert response.url == reverse('core:home')

    def test_logout_shows_success_message(self, authenticated_client):
        """Test that logout shows a success message."""
        response = authenticated_client.get(reverse('accounts:logout'), follow=True)
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) > 0
        assert 'successfully logged out' in str(messages[0]).lower()

    def test_logout_clears_session(self, authenticated_client, test_user):
        """Test that logout properly clears the session."""
        response = authenticated_client.get(reverse('accounts:dashboard'))
        assert response.status_code == 200

        authenticated_client.get(reverse('accounts:logout'))

        response = authenticated_client.get(reverse('accounts:dashboard'))
        assert response.status_code == 302

    def test_logout_page_renders_after_redirect(self, authenticated_client):
        """Test that the page renders correctly after logout (no blank page)."""
        response = authenticated_client.get(reverse('accounts:logout'), follow=True)
        assert response.status_code == 200
        assert b'Kairos' in response.content


@pytest.mark.django_db
class TestNavbarForAdminUsers:
    """Tests for admin navbar display."""

    def test_admin_sees_operations_button(self, db):
        """Test that admin users see Operations button instead of Submit a request."""
        admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            privacy_consent=True,
            terms_accepted=True,
        )
        client = Client()
        client.login(email='admin@test.com', password='adminpass123')
        
        response = client.get(reverse('core:home'))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Operations' in content
        assert 'bi-shield-fill' in content

    def test_client_sees_submit_request_button(self, authenticated_client):
        """Test that non-admin users see Submit a request button."""
        response = authenticated_client.get(reverse('core:home'))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Submit a request' in content
