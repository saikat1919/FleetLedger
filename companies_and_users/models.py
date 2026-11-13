from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, UserManager
from FleetLedger.FleetLedger import settings


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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='company_admin')
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.username} - {self.role}"

class Employee(models.Model):
    EMPLOYEE_TYPE = [
        ("driver", "Driver"),
        ("helper", "Helper"),
        ("manager", "Manager"),
    ]
    PAY_TYPE_CHOICES = [
        ("salary", "Fixed Salary"),
        ("commission", "Commission"),
        ("both", "Salary + Commission")
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='employees'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = PhoneNumberField(
        unique=True,
        blank=True,
        null=True,
    )
    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE,
    )
    pay_type = models.CharField(
        max_length=20,
        choices=PAY_TYPE_CHOICES,
    )
    monthly_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    commission_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    join_date = models.DateField()
    linked_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} -> {self.company.company_name}"
