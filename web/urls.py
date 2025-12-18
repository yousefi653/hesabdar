from django.urls import path
from . import views
urlpatterns = [
    path("account/register/", views.register),
    path("account/login/", views.login),
    path("account/logout/", views.logout),
    path("", views.home),
    path("account/expense/", views.expense),
    path("account/income/", views.income),
    path("account/create_expense/", views.createExpense),
    path("account/create_income/", views.createIncome),
    path("account/update_expense/<int:pk>/", views.updateExpense),
    path("account/delete_expense/<int:pk>/", views.deleteExpense),
    path("account/delete_income/<int:pk>/", views.deleteIncome),
    path("account/update_income/<int:pk>/", views.updateIncome)
]