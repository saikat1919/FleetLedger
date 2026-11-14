from django.core.validators import MinValueValidator
from django.db import models
from FleetLedger.companies_and_users.models import Company
from FleetLedger.fleet.models import Employee
from FleetLedger.FleetLedger import settings


# Create your models here.

class MonthClose(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='month_close')
    year_and_month = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
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
    closed_at = models.DateField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "year_and_month"],
                name="one_month_close_per_company",
            )
        ]
        ordering = ["-year_and_month"]

    def __str__(self):
        return f"Monthly profit -> {self.closed_month_profit}, Closed by {self.closed_by}"


class Payroll(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("finalized", "Finalized"),
        ("paid", "Paid")
    ]
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='payroll')
    month = models.ForeignKey(MonthClose, on_delete=models.SET_NULL, related_name='payroll')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='payroll')
    generated_at = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "month"],
                name="one_payroll_per_company_per_month",
            )
        ]

    def __str__(self):
        pass


class PayrollLine(models.Model):
    payroll_run = models.ForeignKey(Payroll, on_delete=models.SET_NULL, related_name='payroll_line')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='payroll_line')
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    days_present = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    deductions = models.PositiveIntegerField(
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
    payroll_line = models.ForeignKey(PayrollLine, on_delete=models.SET_NULL, related_name='payment_record')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_date = models.DateField()
    method = models.CharField(
        choices=PAYMENT_METHOD_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_line", "paid_date"],
                name="one_record_per_line"
            )
        ]