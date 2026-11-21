from django.contrib import admin
from .models import Employee, Vehicle, VehicleAssignment

# Register your models here.

admin.site.register(Employee)
admin.site.register(Vehicle)
admin.site.register(VehicleAssignment)