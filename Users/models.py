from django.utils import timezone
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserModelManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not password:
            raise ValueError('The given password must be set')

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            is_active=True,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    email_verified_at = models.DateTimeField(
        _('email verified at'),
        null=True,
        blank=True,
        default=None
    )

    email = models.EmailField(
        _("email address"),
        blank=False,
        unique=True,
        null=False
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    country = models.CharField(
        _('country'),
        max_length=255,
        blank=False,
        null=False
    )

    state = models.CharField(
        _('state'),
        max_length=255,
        blank=False,
        null=False
    )

    objects = UserModelManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'country', 'state']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        db_table = 'users'

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name
