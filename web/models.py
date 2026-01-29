from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)


class BankCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    owner = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.card_number} - {self.card_name}"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    jdate = models.CharField(null=True, blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)
    card = models.ForeignKey(BankCard, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"amount:{self.amount}-date:{self.date}"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(blank=True)
    jdate = models.CharField(null=True, blank=True)
    time = models.TimeField(blank=True)
    updated_time = models.DateField(auto_now=True)
    card = models.ForeignKey(BankCard, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"amount:{self.amount}-date:{self.date}"
