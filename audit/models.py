from django.db import models
from django.conf import settings
from FleetLedger.companies_and_users.models import Company

# Create your models here.

class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("created", "Created"),
        ("changed", "Changed"),
        ("deleted", "Deleted"),
        ("closed_month", "Closed Month"),
        ("paid", "Paid"),
        ("login", "Login"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    record_type = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)

    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.record_type}"