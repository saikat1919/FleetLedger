from django.contrib import admin
from .models import MonthClose, Payroll, PayrollLine, PaymentRecord

# Register your models here.

admin.site.register(MonthClose)
admin.site.register(Payroll)
admin.site.register(PayrollLine)
admin.site.register(PaymentRecord)