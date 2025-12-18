from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)