from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from FleetLedger.companies_and_users.models import Company, Employee


# Create your models here.

class Vehicle(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("in_maintenance", "In-Maintenance"),
        ("retired", "Retired")
    ]
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
    )
    registration_number = models.CharField(unique=True, max_length=50)
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
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
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
                fields=["employee"],
                condition=Q(end_date__isnull=True),
                name="one_current_vehicle_per_driver"
            ),
            models.UniqueConstraint(
                condition=(
                    Q(end_date__isnull=True) |
                    Q(end_date__gte=models.F('start_date'))
                ),
                name="assignment_end_after_start_date"
            )
        ]

    def clean(self):
        super().clean()

        if self.vehicle_id and self.company_id:
            if self.vehicle.company_id != self.company_id:
                raise ValidationError(
                    "Vehicle must belong to the selected company."
                )

        if self.employee_id and self.company_id:
            if self.employee.company_id != self.company_id:
                raise ValidationError(
                    "Employee must belong to the selected company."
                )

        if self.employee_id:
            if self.employee.employee_type != "driver":
                raise ValidationError(
                    "Only employees with the Driver type can be assigned."
                )

        if self.vehicle_id and self.vehicle.status == "retired":
            raise ValidationError(
                "A retired vehicle cannot be assigned."
            )

        if self.employee_id and not self.employee.is_active:
            raise ValidationError(
                "An inactive employee cannot be assigned."
            )

        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    "End date cannot be earlier than start date."
                )

    def __str__(self):
        return (
            f"{self.employee.name} - "
            f"{self.vehicle.registration_number}"
        )

