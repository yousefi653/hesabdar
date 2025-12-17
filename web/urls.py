from django.urls import path
from . import views
urlpatterns = [
    path("account/register/", views.register),
    path("account/login/", views.login),
    path("account/logout/", views.logout),
    path("home/", views.home),
    path("account/expense/", views.expense),
    path("account/income/", views.income),
    path("account/create_expense/", views.createExpense),
    path("account/create_income/", views.createIncome)
]