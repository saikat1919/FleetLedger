from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=200)
    contact_person_first_name = models.CharField(max_length=100)
    contact_person_last_name = models.CharField(max_length=100)
    contact_person_email = models.EmailField()
    contact_person_phone = models.CharField()