from django.core.validators import MinValueValidator
from django.db import models
from FleetLedger.companies_and_users.models import Company, Employee
from FleetLedger.fleet.models import Vehicle
# Create your models here.


class ExpenseCategory(models.Model):
    EXPENSE_CHOICES = [
        ("fuel", "Fuel"),
        ("toll", "Toll"),
        ("repair and maintenance", "Repair and Maintenance"),
        ("driver allowance", "Driver Allowance"),
        ("police or fine payments", "Police or fine payments"),
        ("others", "Others"),
    ]
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name="expense_category")
    name = models.CharField(
        max_length=100,
        choices=EXPENSE_CHOICES,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_expense_category",
            )
        ]

    def __str__(self):
        return f"Expense type: {self.name}"

class DailyEntry(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
    ]

    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name="daily_entries")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name="daily_entries")
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name="daily_entries")
    date = models.DateField()
    income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    vehicle_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    commission_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default="draft"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle", "date"],
                name="unique_daily_entry_per_vehicle",
            )
        ]

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.date}"


class DailyExpenseLine(models.Model):
    daily_entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE)
    expense_category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        pass






