from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    jdate = models.CharField(null=True, blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    jdate = models.CharField(null=True, blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)

    def __str__(self):
        return f"amount:{self.amount}-date:{self.date}"