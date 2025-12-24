from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import User, Expense, Income
from .forms import *
import jdatetime
import datetime
import secrets
import time
import os
import smtplib
from email.mime.text import MIMEText


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


def send_email(email, code):
    sender = "yousef.devmev@gmail.com"
    password = os.getenv("EMAIL_APP_PASSWORD")
    receiver = email

    today = jdatetime.date.today()
    now = jdatetime.datetime.now().time()
    msg = MIMEText(f"کد احراز هویت شما: {code}\nتاریخ: {today.strftime("%Y/%m/%d")}\nزمان: {now.strftime("%H:%M:%S")}\nکد بعد از 2 دقیقه منقضی میشود.")
    msg["Subject"] = "کد احراز هویت"
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP(host="smtp.gmail.com", port=587, timeout=20)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()


def gen_code():
    return f"{secrets.randbelow(1_000_000):06d}"


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            code = gen_code()
            send_email(form.cleaned_data.get("email"), code)
            request.session["register"] = {
                "username": form.cleaned_data.get("username"),
                "email": form.cleaned_data.get("email"),
                "password": form.cleaned_data.get("password1"),
                "code": code,
                "expire_time": time.time() + 120
            }
            return redirect("/account/verify_person/")
    else:
        form = RegisterForm()
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'register.html', context={'form':form})
        

@csrf_exempt
def verify_person(request):
    if request.method == "POST":
        verify_code= request.session.get("register")['code']
        expire_time = request.session.get('register')['expire_time']
        form = VerifyCodeForm(request.POST, verify_code=verify_code, expire_time=expire_time)
        if form.is_valid():
            username = request.session.get("register")["username"]
            email = request.session.get("register")["email"]
            password = request.session.get("register")['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            return redirect("/")
        
        if time.time() > expire_time:
            username = request.session.get("register")["username"]
            email = request.session.get("register")["email"]
            password = request.session.get("register")['password']
            request.session.pop("register", None)
            code = gen_code()
            send_email(email, code)
            request.session["register"] = {
                "username": username,
                "email": email,
                "password": password,
                "code": code,
                "expire_time": time.time() + 120
            }
    else:
        form = VerifyCodeForm()
    return render(request, "verifyperson.html", {"form": form})
        

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
        contenxt = {"data": data, "title_fa": "خرج", "title_en": "expense", 'url_delete': 'delete_expense'}
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


@csrf_exempt
@login_required(login_url="/account/login/")
def profile(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("/account/profile/")
    else:
        form = ProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form})


@csrf_exempt
@login_required(login_url="/account/login/")
def changePassword(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, instance=user)
        if form.is_valid():
            new_password = form.cleaned_data.get("p1")
            code = gen_code()
            send_email(user.email, code)
            request.session["verify_password"] = {"password": new_password, "code": code, "expire_time": time.time() + 120}
            return redirect("/account/verify_code/")
    else:
        form = ChangePasswordForm(instance=user)
    return render(request, "changepassword.html", {"form":form})


@csrf_exempt
@login_required(login_url="/account/login/")
def verify_password(request):
    if request.method == "POST":
        code = request.session.get("verify_password")['code']
        expire_time = request.session.get("verify_password")["expire_time"]
        form = VerifyCodeForm(request.POST, verify_code=code, expire_time=expire_time)
        if form.is_valid():
            user = request.user
            user.set_password(request.session.get("verify_password")["password"])
            user.save()
            return redirect("/account/logout/")
        if time.time() > expire_time:
            new_password = request.session.get("verify_password")['password']
            code = gen_code()
            send_email(request.user.email, code)
            request.session.pop('verify_password', None)
            request.session["verify_password"] = {"password": new_password, "code": code, "expire_time": time.time() + 120}
    else:
        form = VerifyCodeForm()
    return render(request, "verifypage.html", {"form":form})


@csrf_exempt
@login_required(login_url="/account/login/")
def deleteaccount(request):
    if request.method == "POST":
        code = gen_code()
        send_email(request.user.email, code)
        request.session["delete_account"] = {
            "code": code,
            "expire_time": time.time() + 120
        }
        return redirect("/account/verify_delete_account/")

    return HttpResponseNotFound()


@csrf_exempt
@login_required(login_url="/account/login/")
def verify_DeleteAccount(request):
    if request.method == "POST":
        code = request.session.get("delete_account")['code']
        expire_time = request.session.get("delete_account")['expire_time']
        form = VerifyCodeForm(request.POST, verify_code=code, expire_time=expire_time)
        if form.is_valid():
            user = request.user
            User.objects.get(username=user.username).delete()
            return redirect("/account/logout/")
        if time.time() > expire_time:
            request.session.pop("delete_account")
            code = gen_code()
            send_email(request.user.email, code)
            request.session["delete_account"] = {
            "code": code,
            "expire_time": time.time() + 120
        }
    else:
        form = VerifyCodeForm()
    return render(request, "verifydeleteaccount.html", {"form": form})


