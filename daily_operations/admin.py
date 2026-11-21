from django.contrib import admin
from .models import ExpenseCategory, DailyEntry, DailyExpenseLine

# Register your models here.

admin.site.register(ExpenseCategory)
admin.site.register(DailyEntry)
admin.site.register(DailyExpenseLine)