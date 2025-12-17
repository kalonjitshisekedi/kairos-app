"""
Custom user model with roles for Kairos platform.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        EXPERT = 'expert', 'Expert'
        ADMIN = 'admin', 'Admin'

    class ClientStatus(models.TextChoices):
        PENDING = 'pending', 'Pending verification'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    class ExpertStatusChoices(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        VETTED = 'vetted', 'Vetted'
        ACTIVE = 'active', 'Active'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    client_status = models.CharField(
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.PENDING,
        help_text='Client approval status'
    )
    expert_status = models.CharField(
        max_length=20,
        choices=ExpertStatusChoices.choices,
        default=ExpertStatusChoices.APPLIED,
        help_text='Expert approval status'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    privacy_consent = models.BooleanField(default=False)
    privacy_consent_date = models.DateTimeField(blank=True, null=True)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(blank=True, null=True)
    deletion_requested = models.BooleanField(default=False)
    deletion_requested_date = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_expert(self):
        return self.role == self.Role.EXPERT

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class AuditLog(models.Model):
    class EventType(models.TextChoices):
        USER_CREATED = 'user_created', 'User created'
        USER_LOGIN = 'user_login', 'User login'
        USER_LOGOUT = 'user_logout', 'User logout'
        PASSWORD_RESET = 'password_reset', 'Password reset'
        PROFILE_UPDATED = 'profile_updated', 'Profile updated'
        VERIFICATION_STATUS_CHANGED = 'verification_changed', 'Verification status changed'
        BOOKING_CREATED = 'booking_created', 'Booking created'
        BOOKING_STATUS_CHANGED = 'booking_status_changed', 'Booking status changed'
        PAYMENT_RECEIVED = 'payment_received', 'Payment received'
        PAYMENT_REFUNDED = 'payment_refunded', 'Payment refunded'
        FILE_UPLOADED = 'file_uploaded', 'File uploaded'
        FILE_DOWNLOADED = 'file_downloaded', 'File downloaded'
        ADMIN_ACTION = 'admin_action', 'Admin action'
        DELETION_REQUESTED = 'deletion_requested', 'Deletion requested'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_audit_log'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} - {self.user} - {self.created_at}'


class ExpertInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'accounts_expert_invitation'

    def __str__(self):
        return f'Invitation for {self.email}'

    @property
    def is_valid(self):
        return not self.used and self.expires_at > timezone.now()
