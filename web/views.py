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
def clean(data):
    for item in data:
        item.amount = f"{item.amount:,}"
        item.date = jdatetime.date.fromgregorian(date=item.date)
        item.date = jdatetime.datetime.strftime(item.date, "%Y/%m-%b/%d-%a")
        item.time = datetime.time.strftime(item.time, "%I:%M-%p")
    return data


def get_queryset(request, data):
    q = request.GET.get('title')
    if q:
        data = data.filter(title__contains = q)
    
    q = request.GET.get("amount")
    if q:
        q = int(q)
        if q > 0:
            data = data.filter(amount__gte=q)
        else:
            data = data.filter(amount__lte=q*-1)
    
    q = request.GET.get("sort_date")
    if q:
        if q == 'date':
            data = data.order_by("date")
        elif q == '-date' :
            data = data.order_by('-date')
        else:
            pass
    
    q = request.GET.get("sort_id")
    if q:
        if q == 'id':
            data = data.order_by('id')
        elif q == '-id':
            data = data.order_by("-id")
        else:
            pass

    return data


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="/")

    else:
        form = RegisterForm()
    if request.user.is_authenticated:
        return redirect("/")
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
                return redirect(to="/")
    else:
        form = LoginForm()
    if request.user.is_authenticated:
        return redirect("/")
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
        user = request.user
        data = Expense.objects.filter(user=user)
        data = get_queryset(request, data)
        data = clean(data)       
        contenxt = {"data": data, "title": "خرج ها"}
        return render(request, 'flowdetail.html', contenxt)
    

@csrf_exempt
@login_required(login_url="/account/login/")
def income(request):
    if request.method == "GET":
        user = request.user
        data = Income.objects.filter(user=user)
        data = get_queryset(request, data)
        data = clean(data)
        contenxt = {"data": data, "title": "درآمدها"}
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
    
            