from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import User, Expense, Income
from .forms import RegisterForm, LoginForm, ExpenseIncomeForm
import jdatetime
import datetime

# Create your views here.
def clean_number(data):
    for item in data:
        item.amount = f"{item.amount:,}"
    return data



@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="/home/")

    else:
        form = RegisterForm()
    return render(request, 'register.html', context={'form':form})
        

@csrf_exempt
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user:
                dj_login(request, user=user)
                return redirect(to="/home/")
    else:
        form = LoginForm()
    return render(request, 'login.html', context={"form": form})

@csrf_exempt
@login_required(login_url='/account/login/')
def logout(request):
    if request.method == "GET":
        dj_logout(request)
        return redirect(to="/account/login/")
    


@login_required(login_url="/account/login/")
def home(request):
    if request.method == "GET":
        return render(request, 'home.html')
    

@csrf_exempt
@login_required(login_url="/account/login/")
def expense(request):
    if request.method == "GET":
        data = Expense.objects.all()
        for item in data:
            item.date = jdatetime.date.fromgregorian(date=item.date)
            item.date = jdatetime.datetime.strftime(item.date, "%Y/%m-%b/%d-%a")
            item.time = datetime.time.strftime(item.time, "%I:%M-%p")
        data = clean_number(data)
        contenxt = {"data": data, "title": "Expense"}
        return render(request, 'flowdetail.html', contenxt)
    

@csrf_exempt
@login_required(login_url="/account/login/")
def income(request):
    if request.method == "GET":
        data = Income.objects.all()
        for item in data:
            item.date = jdatetime.date.fromgregorian(date=item.date)
            item.date = jdatetime.datetime.strftime(item.date, "%Y/%m-%b/%d-%a")
            item.time = datetime.time.strftime(item.time, "%I:%M-%p")
        data = clean_number(data)
        contenxt = {"data": data, "title": "Income"}
        return render(request, 'flowdetail.html', contenxt)
    

@csrf_exempt
@login_required(login_url="/account/login/")
def createExpense(request):
    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data.get('title')
            text = form.cleaned_data.get('text')
            amount = form.cleaned_data.get("amount")
            date = form.cleaned_data.get('date')
            time = form.cleaned_data.get("time")
            expense = Expense.objects.create(user=user, title=title, text=text, amount=amount, date=date, time=time)
            if expense:
                return redirect(to="/account/expense/")
    else:
        form = ExpenseIncomeForm()
    context = {"form": form, 'title': "خرج"}
    return render(request, 'flowcash.html', context=context)
    
            

@csrf_exempt
@login_required(login_url="/account/login/")
def createIncome(request):
    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data.get('title')
            text = form.cleaned_data.get('text')
            amount = form.cleaned_data.get("amount")
            date = form.cleaned_data.get('date')
            time = form.cleaned_data.get("time")

            expense = Income.objects.create(user=user, title=title, text=text, amount=amount, date=date, time=time)
            if expense:
                return redirect(to="/account/income/")
    else:
        form = ExpenseIncomeForm()
    context = {"form": form, 'title': "درآمد"}
    return render(request, 'flowcash.html', context=context)
    
            