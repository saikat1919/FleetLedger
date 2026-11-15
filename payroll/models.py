from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from companies_and_users.models import Company
from fleet.models import Employee
from django.conf import settings


# Create your models here.

class MonthClose(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='month_close')
    month = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="open"
    )
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    closed_month_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='closed_months',
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "month"],
                name="one_month_close_per_company",
            ),
            models.CheckConstraint(
                condition=Q(status='open', closed_by__isnull=True, closed_at__isnull=True) |
                        Q(status='closed', closed_by__isnull=False, closed_at__isnull=False),
                name="closed_month_has_closer"
            )
        ]
        ordering = ["-month"]

    def __str__(self):
        return f"Monthly profit -> {self.closed_month_profit}, Closed by {self.closed_by}"


class Payroll(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("finalized", "Finalized"),
        ("paid", "Paid")
    ]
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='payroll')
    month = models.ForeignKey(MonthClose, on_delete=models.PROTECT, related_name='payroll')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payroll')
    generated_at = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "month"],
                name="one_payroll_per_company_per_month",
            )
        ]




class PayrollLine(models.Model):
    payroll_run = models.ForeignKey(Payroll, on_delete=models.PROTECT, related_name='payroll_line')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payroll_line')
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    days_present = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run", "employee"],
                name="one_line_per_employee_per_run",
            )
        ]


class PaymentRecord(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("mobile_banking", "Mobile Banking"),
    ]
    payroll_line = models.OneToOneField(PayrollLine, on_delete=models.PROTECT, related_name='payment_record')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    paid_date = models.DateField()
    method = models.CharField(
        choices=PAYMENT_METHOD_CHOICES,
        max_length=20
    )
    created_at = models.DateTimeField(auto_now_add=True)


