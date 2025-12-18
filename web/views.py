from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import User, Expense, Income
from .forms import RegisterForm, LoginForm, ExpenseIncomeForm
import jdatetime
import datetime

# Create your views here.
def clean(data):
    for item in data:
        item.amount = f"{item.amount:,}"
        item.date = jdatetime.date.fromgregorian(date=item.date)
        item.date = jdatetime.datetime.strftime(item.date, "%Y/%m/%d")
        item.time = datetime.time.strftime(item.time, "%I:%M-%p")
        item.updated_time = jdatetime.date.fromgregorian(date=item.updated_time)
        item.updated_time = jdatetime.datetime.strftime(item.updated_time, "%Y/%m/%d")
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
        contenxt = {"data": data, "title_fa": "خرج", "title_en": "expense"}
        return render(request, 'flowdetail.html', contenxt)
    

@csrf_exempt
@login_required(login_url="/account/login/")
def income(request):
    if request.method == "GET":
        user = request.user
        data = Income.objects.filter(user=user)
        data = get_queryset(request, data)
        data = clean(data)
        contenxt = {"data": data, "title_fa": "درآمد", "title_en":"income", 'url_delete':'delete_income'}
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
            date = form.cleaned_data.get('date') or datetime.date.today()
            time = form.cleaned_data.get("time") or datetime.datetime.now().time()
            expense = Expense.objects.create(user=user, title=title, text=text, amount=amount, date=date, time=time)
            if expense:
                return redirect(to="/account/expense/")
    else:
        now = datetime.datetime.now()
        form = ExpenseIncomeForm(initial={"date": now.date(), "time": now.time()})
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
            date = form.cleaned_data.get('date') or datetime.date.today()
            time = form.cleaned_data.get("time") or datetime.datetime.now().time()
            expense = Income.objects.create(user=user, title=title, text=text, amount=amount, date=date, time=time)
            if expense:
                return redirect(to="/account/income/")
    else:
        now = datetime.datetime.now()
        form = ExpenseIncomeForm(initial={"date": now.date(), "time": now.time()})
    context = {"form": form, 'title': "درآمد"}
    return render(request, 'flowcash.html', context=context)
    

@csrf_exempt    
@login_required(login_url="/account/login/")
def updateExpense(request, pk):
    user = request.user
    expense = get_object_or_404(Expense, user=user, pk=pk)

    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST)
        if form.is_valid():
            expense.title = form.cleaned_data.get('title')
            expense.text = form.cleaned_data.get('text')
            expense.amount = form.cleaned_data.get("amount")
            expense.date = form.cleaned_data.get('date')
            expense.time = form.cleaned_data.get("time")
            expense.save()
            return redirect("/account/expense/")
    else:
        form = ExpenseIncomeForm(instance=expense)
    return render(request, 'flowupdate.html', {"form":form, "title_fa": 'خرج', 'title_en': 'expense'})


@csrf_exempt
@login_required(login_url="/account/login/")
def deleteExpense(request, pk):
    user = request.user
    expense = get_object_or_404(
        Expense,
        user=user,
        pk=pk
    )
    if request.method == "POST":
        expense.delete()
        return redirect("/account/expense/")
    return HttpResponseNotFound()


@csrf_exempt    
@login_required(login_url="/account/login/")
def updateIncome(request, pk):
    user = request.user
    income = get_object_or_404(Income, user=user, pk=pk)

    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST)
        if form.is_valid():
            income.title = form.cleaned_data.get('title')
            income.text = form.cleaned_data.get('text')
            income.amount = form.cleaned_data.get("amount")
            income.date = form.cleaned_data.get('date')
            income.time = form.cleaned_data.get("time")
            income.save()
            return redirect("/account/income/")
    else:
        form = ExpenseIncomeForm(instance=income)
    return render(request, 'flowupdate.html', {"form":form, "title_fa": 'درآمد'})


@csrf_exempt
@login_required(login_url="/account/login/")
def deleteIncome(request, pk):
    user = request.user
    income = get_object_or_404(
        Income,
        user=user,
        pk=pk
    )
    if request.method == "POST":
        income.delete()
        return redirect("/account/income/")
    return HttpResponseNotFound()