from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, UserManager


# Create your models here.

class Company(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person_first_name = models.CharField(max_length=100)
    contact_person_last_name = models.CharField(max_length=100)
    contact_person_email = models.EmailField()
    contact_person_phone = PhoneNumberField(
        unique=True,
        blank=True,
        null=True,
    )
    contact_person_address = models.TextField(max_length=500)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name}-Represented by {self.contact_person_first_name} {self.contact_person_last_name}"


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None,
                         password=None, **extra_fields):
        extra_fields["role"] = "platform_admin"

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

class User(AbstractUser):
    ROLE_CHOICES = [
        ('company_admin', 'Admin'),
        ('company_manager', 'Manager'),
        ('platform_admin', 'Platform Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='company_manager')
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(role='platform_admin', company__isnull=True) |
                          (~Q(role='platform_admin') & Q(company__isnull=False)),
                name='platform_admin_has_no_company'
            )
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.username} - {self.role}"


