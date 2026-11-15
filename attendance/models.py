from django.db import models
from FleetLedger.companies_and_users.models import Company
from FleetLedger.fleet.models import Employee

# Create your models here.

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("leave", "Leave"),
        ("half-day", "Half Day"),
    ]
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name="attendance")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="attendance")
    date = models.DateField()
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="one_record_per_employee",
            )
        ]

    def __str__(self):
        return f"{self.employee.first_name}: {self.status}"