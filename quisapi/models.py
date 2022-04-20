import uuid as uuid_lib

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class QuisAPIUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class QuisAPIUser(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        primary_key=True,
        editable=False
    )
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
        blank=True,
        null=True
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
        blank=True,
        null=True
    )
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': "A user with that email already exists.",
        },
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    creation_date = models.DateTimeField(
        'date joined',
        default=timezone.now
    )
    update_date = models.DateTimeField(
        'update date',
        auto_now=True
    )

    objects = QuisAPIUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = False

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class QuizGroup(models.Model):
    class Meta:
        verbose_name = 'QuizGroup'
        verbose_name_plural = 'QuizGroup'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'quiz_group_name'],
                name='quiz_group_name_unique'
            ),
        ]

    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        QuisAPIUser,
        on_delete=models.CASCADE,
    )
    quiz_group_name = models.CharField(
        max_length=64,
    )
    quiz_group_description = models.TextField(
        blank=True,
    )
    scope = models.BooleanField(
        default=False,
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
    )
    update_date = models.DateTimeField(
        auto_now=True,
    )


class Quiz(models.Model):
    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'

    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        primary_key=True,
        editable=False,
    )
    quiz_group = models.ForeignKey(
        QuizGroup,
        on_delete=models.CASCADE,
    )
    quiz_title = models.CharField(
        max_length=128,
    )
    quiz_content = models.CharField(
        max_length=1024,
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
    )
    update_date = models.DateTimeField(
        auto_now=True,
    )


class Follow(models.Model):
    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follow'

    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        primary_key=True,
        editable=False,
    )
    quiz_group = models.ForeignKey(
        QuizGroup,
        on_delete=models.CASCADE,
    )
    followings = models.IntegerField(
        default=0,
    )
