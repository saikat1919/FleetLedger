from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator
from FleetLedger.companies_and_users.models import Company
from phonenumber_field.modelfields import PhoneNumberField
from FleetLedger.FleetLedger import settings


# Create your models here.

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
        max_digits=5,
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


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("in_maintenance", "In-Maintenance"),
        ("retired", "Retired")
    ]
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True
    )
    registration_number = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'registration_number'],
                name='unique_registration_number_per_company'
            )
        ]
        ordering = ['-created_at']

class VehicleAssignment(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vehicle_assignments'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        related_name="vehicle_assignments"
    )
    driver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vehicle_assignments',
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(end_date__isnull=True),
                name="one_unique_driver_per_vehicle"
            ),
            models.UniqueConstraint(
                fields=["driver"],
                condition=Q(end_date__isnull=True),
                name="one_current_vehicle_per_driver"
            ),
            models.CheckConstraint(
                condition=(
                        Q(end_date__isnull=True) |
                        Q(end_date__gte=models.F("start_date"))
                ),
                name="assignment_end_after_start_date"
            )
        ]

    def __str__(self):
        return (
            f"{self.driver.first_name} {self.driver.last_name} - "
            f"{self.vehicle.registration_number}"
        )

