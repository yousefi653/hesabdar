from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django.views import generic
from django.conf import settings
from django.db.models import Sum, Max
from .models import User, Expense, Income
from .forms import *
import jdatetime
import datetime
import secrets
import time
import os
import smtplib
from email.mime.text import MIMEText
from matplotlib import pyplot



# Create your views here.
def get_today(request):
    today = jdatetime.date.today()
    return {"today": jdatetime.date.strftime(today, "%Y/%m/%d")}


def clean(data):
    for item in data:
        item.amount = f"{item.amount:,}"
        item.date = datetime.datetime.strftime(item.date, "%Y/%m/%d")
        item.time = datetime.time.strftime(item.time, "%I:%M-%p")
        item.updated_time = jdatetime.date.fromgregorian(date=item.updated_time)
        item.updated_time = jdatetime.datetime.strftime(item.updated_time, "%Y/%m/%d")
    return data


def get_queryset(request, data):

    q = request.GET.get("title")
    if q:
        data = data.filter(title__contains=q)

    q = request.GET.get("amount")
    if q:
        q = int(q)
        if q > 0:
            data = data.filter(amount__gte=q)
        else:
            data = data.filter(amount__lte=q * -1)

    q = request.GET.get("date")
    if q:
        if q == "date":
            data = data.order_by("date")
        elif q == "-date":
            data = data.order_by("-date")
        else:
            data = data.order_by("date")

    return data


def send_email(email, code):
    sender = "yousef.devmev@gmail.com"
    password = os.getenv("EMAIL_APP_PASSWORD")
    receiver = email

    today = jdatetime.date.today()
    now = jdatetime.datetime.now().time()
    msg = MIMEText(
        f"کد احراز هویت شما: {code}\nتاریخ: {today.strftime("%Y/%m/%d")}\nزمان: {now.strftime("%H:%M:%S")}\nکد بعد از 2 دقیقه منقضی میشود."
    )
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


def draw_plot(user, card):
    today = jdatetime.date.today()
    day_in_month = jdatetime.j_days_in_month[today.month - 1]

    incomes = Income.objects.filter(user=user, card=card, jdate__contains=f"/{today.month}/")
    temp = [0 for _ in range(day_in_month)]
    for day in range(1, day_in_month + 1):
        sum = incomes.filter(jdate__contains=f"{today.month}/{day:02d}").aggregate(sum=Sum("amount"))
        if sum['sum']:
            temp[day-1] = sum['sum']
    del incomes
    incomes = temp.copy()

    expenses = Expense.objects.filter(user=user, card=card, jdate__contains=f"/{today.month}/")
    temp = [0 for _ in range(day_in_month)]
    for day in range(1, day_in_month + 1):
        sum = expenses.filter(jdate__contains=f"{today.month}/{day:02d}").aggregate(sum=Sum('amount'))
        if sum['sum']:
            temp[day-1] = sum['sum']
    del expenses
    expenses = temp.copy()

    ## یکسری امار معمولی
    total_incomes = Income.objects.filter(user=user, card=card).aggregate(sum=Sum("amount"))['sum'] or 0
    total_expenses = Expense.objects.filter(user=user, card=card).aggregate(sum=Sum('amount'))['sum'] or 0
    balance = total_incomes - total_expenses
    ave_daily_income = total_incomes / today.day or 0
    ave_daily_expense = total_expenses / today.day or 0
    max_income = Income.objects.filter(user=user, card=card).aggregate(max=Max("amount"))['max'] or 0
    max_expense = Expense.objects.filter(user=user, card=card).aggregate(max=Max("amount"))['max'] or 0

    contenxt = {"total_incomes": f"{total_incomes:,}",
                "total_expense": f"{total_expenses:,}",
                "balance": f"{balance:,}",
                "ave_daily_income": f"{ave_daily_income:,.2f}",
                "ave_daily_expense": f"{ave_daily_expense:,.2f}",
                "max_income": f"{max_income:,}",
                "max_expense": f"{max_expense:,}"
                }
    ## تمام


    days = [x for x in range(1, day_in_month +1 )]
    pyplot.figure(figsize=(10, 7))
    pyplot.plot(days, incomes, color="green", marker="o", linewidth=3, markersize=5)
    pyplot.plot(days, expenses, color="red", marker="o", linewidth=3, markersize=5)
    pyplot.xlabel("Days of the month", fontsize=12, fontweight='bold')
    pyplot.ylabel("Amount", fontsize=12, fontweight='bold')
    pyplot.title("Income and expense chart", fontsize=15, fontweight='bold', color='blue')
    pyplot.xticks(days, rotation=45, fontsize=9)
    pyplot.grid(True)
    pyplot.savefig(f"{settings.BASE_DIR}/web/static/web/img/chart.png", dpi=100, bbox_inches='tight')
    pyplot.close()
    
    return contenxt

def verify_code(request):
    purpose = request.session.get("verify")["purpose"]
    if ((purpose == "register") and (not request.user.is_authenticated)) or (
        request.user.is_authenticated and purpose != "register"):
        if request.method == "POST":
            code = request.session.get("verify")["code"]
            expire_time = request.session.get("verify")["expire_time"]
            form = VerifyCodeForm(
                request.POST, verify_code=code, expire_time=expire_time
            )

            if form.is_valid():
                if purpose == "register":
                    username = request.session.get("verify")["username"]
                    user = User.objects.get(username=username)
                    user.is_active = True
                    user.save()
                    request.session.pop("verify", None)
                    dj_login(request, user)
                    return redirect("/")

                elif purpose == "change_password":
                    request.session.pop("verify", None)
                    request.session["user_verified"] = {
                        "username": request.user.username,
                        "expire_time": time.time() + 300
                    }
                    return redirect("/account/change_password/")

                elif purpose == "delete_account":
                    username = request.session.get("verify")["username"]
                    user = User.objects.get(username=username)
                    user.delete()
                    request.session.pop("verify", None)
                    return redirect("/account/logout/")

            if time.time() > expire_time:
                session = request.session.get("verify")
                request.session.pop("verify", None)
                code = gen_code()
                send_email(session["email"], code)
                session["code"] = code
                session["expire_time"] = time.time() + 120
                request.session["verify"] = session
        else:
            form = VerifyCodeForm()
        return render(request, "verifypage.html", {"form": form})
    return HttpResponseForbidden()


@ratelimit(key='ip', rate="3/h", block=True)
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            User.objects.create_user(
                username=username, email=email, password=password, is_active=False
            )
            code = gen_code()
            send_email(email, code)
            request.session["verify"] = {
                "purpose": "register",
                "username": username,
                "email": email,
                "code": code,
                "expire_time": time.time() + 120,
            }
            return redirect("/account/verify_code/")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@ratelimit(key="ip", rate="5/m", block=True)
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
    return render(request, "login.html", context={"form": form})


@login_required(login_url="/account/login/")
def logout(request):
    if request.method == "POST":
        dj_logout(request)
        return redirect(to="/account/login/")
    return HttpResponseForbidden()


@login_required(login_url="/account/login/")
def home(request):
    if request.method == "GET":
        try: 
            card = BankCard.objects.filter(user=request.user)[0]
        except IndexError:
            pass
        return render(request, "home.html")


@login_required(login_url="/account/login/")
def expense(request):
    if request.method == "GET":
        user = request.user
        card_id = request.GET.get("card_id")
        if card_id:
            card = BankCard.objects.get(id=card_id, user=user)
        else:
            card = BankCard.objects.filter(user=user).first()

        data = Expense.objects.filter(user=user, card=card)
        data = get_queryset(request, data)  
        data = clean(data)
        contenxt = {
            "cards": BankCard.objects.filter(user=request.user),
            "data": data,
            "title_fa": "خرج",
            "title_en": "expense",
            "url_delete": "delete_expense",
        }
        return render(request, "flowdetail.html", contenxt)


@login_required(login_url="/account/login/")
def income(request):
    if request.method == "GET":
        user = request.user
        if request.GET.get("card_id"):
            card = BankCard.objects.get(id=request.GET.get("card_id"), user=user)
        else:
            card = BankCard.objects.filter(user=user).first()
        data = Income.objects.filter(user=user, card=card)
        data = get_queryset(request, data)
        data = clean(data)
        contenxt = {
            "cards": BankCard.objects.filter(user=request.user),
            "data": data,
            "title_fa": "درآمد",
            "title_en": "income",
            "url_delete": "delete_income",
        }
        return render(request, "flowdetail.html", contenxt)


@ratelimit(key="user", rate="10/m", block=True)
@login_required(login_url="/account/login/")
def createExpense(request):
    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data.get("title")
            text = form.cleaned_data.get("text")
            amount = form.cleaned_data.get("amount")
            date = form.cleaned_data.get("date") or datetime.date.today()
            jdate = jdatetime.date.fromgregorian(date=date).strftime("%Y/%m/%d")
            time = form.cleaned_data.get("time") or datetime.datetime.now().time()
            card = form.cleaned_data.get("card")
            expense = Expense.objects.create(
                user=user, title=title, text=text, amount=amount, date=date, time=time, jdate=jdate, card=card
            )
            if expense:
                return redirect(to="/account/expense/")
    else:
        now = datetime.datetime.now()
        form = ExpenseIncomeForm(initial={"date": now.date(), "time": now.time()}, user=request.user)
    context = {"form": form, "title": "خرج"}
    return render(request, "flowcash.html", context=context)


@ratelimit(key="user", rate="10/m", block=True)
@login_required(login_url="/account/login/")
def createIncome(request):
    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data.get("title")
            text = form.cleaned_data.get("text")
            amount = form.cleaned_data.get("amount")
            date = form.cleaned_data.get("date") or datetime.date.today()
            jdate = jdatetime.date.fromgregorian(date=date).strftime("%Y/%m/%d")
            time = form.cleaned_data.get("time") or datetime.datetime.now().time()
            card = form.cleaned_data.get("card")
            expense = Income.objects.create(
                user=user, title=title, text=text, amount=amount, date=date, time=time, jdate=jdate, card=card
            )
            if expense:
                return redirect(to="/account/income/")
    else:
        now = datetime.datetime.now()
        form = ExpenseIncomeForm(initial={"date": now.date(), "time": now.time()}, user=request.user)
    context = {"form": form, "title": "درآمد"}
    return render(request, "flowcash.html", context=context)


@ratelimit(key="user", rate="6/m", block=True)
@login_required(login_url="/account/login/")
def updateExpense(request, pk):
    user = request.user
    expense = get_object_or_404(Expense, user=user, pk=pk)

    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST, user=user)
        if form.is_valid():
            expense.title = form.cleaned_data.get("title")
            expense.text = form.cleaned_data.get("text")
            expense.amount = form.cleaned_data.get("amount")
            expense.date = form.cleaned_data.get("date")
            expense.jdate = jdatetime.date.fromgregorian(date=expense.date).strftime("%Y/%m/%d")
            expense.time = form.cleaned_data.get("time")
            expense.save()
            return redirect("/account/expense/")
    else:
        form = ExpenseIncomeForm(instance=expense, user=user)
    return render(
        request,
        "flowupdate.html",
        {"form": form, "title_fa": "خرج", "title_en": "expense"},
    )


@login_required(login_url="/account/login/")
def deleteExpense(request, pk):
    user = request.user
    expense = get_object_or_404(Expense, user=user, pk=pk)
    if request.method == "POST":
        expense.delete()
        return redirect("/account/expense/")
    return HttpResponseNotFound()


@ratelimit(key='user', rate="6/m", block=True)
@login_required(login_url="/account/login/")
def updateIncome(request, pk):
    user = request.user
    income = get_object_or_404(Income, user=user, pk=pk)

    if request.method == "POST":
        form = ExpenseIncomeForm(request.POST, user=user)
        if form.is_valid():
            income.title = form.cleaned_data.get("title")
            income.text = form.cleaned_data.get("text")
            income.amount = form.cleaned_data.get("amount")
            income.date = form.cleaned_data.get("date")
            income.jdate = jdatetime.date.fromgregorian(date=income.date).strftime("%Y/%m/%d")
            income.time = form.cleaned_data.get("time")
            income.save()
            return redirect("/account/income/")
    else:
        form = ExpenseIncomeForm(instance=income, user=user)
    return render(request, "flowupdate.html", {"form": form, "title_fa": "درآمد", "title_en": "income"})


@login_required(login_url="/account/login/")
def deleteIncome(request, pk):
    user = request.user
    income = get_object_or_404(Income, user=user, pk=pk)
    if request.method == "POST":
        income.delete()
        return redirect("/account/income/")
    return HttpResponseNotFound()


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
        cards = BankCard.objects.filter(user=request.user)
    return render(request, "profile.html", {"form": form, "cards": cards})


@ratelimit(key='user', rate="3/h", block=True)
@login_required(login_url="/account/login/")
def request_changePassword(request):
    if request.method == "POST":
        request.session.pop("verify", None)
        email = request.user.email
        code = gen_code()
        send_email(email, code)
        request.session["verify"] = {
            "purpose": "change_password",
            "email": email,
            "code": code,
            "expire_time": time.time() + 120,
        }
        return redirect("/account/verify_code/")
    return HttpResponseForbidden()


@login_required(login_url="/account/login/")
def changePassword(request):
    user = request.user
    verify = request.session.get("user_verified")
    if not verify:
        return HttpResponseForbidden("شما احراز هویت نشده اید.")
    if verify['username'] !=  user.username:
        return HttpResponseForbidden("نام کاربری شما احراز هویت نشده است.")
    if time.time() > verify['expire_time']:
        return HttpResponseForbidden("از اخرین احراز هویت شما 5 دقیقه میگذره دوباره احراز هویت کن")
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, instance=user)
        if form.is_valid():
            password = form.cleaned_data.get("p1")
            temp = User.objects.get(username=user.username)
            temp.set_password(password)
            temp.save()
            request.session.pop("user_verified", None)
            return redirect("/account/logout/")
    else:
        form = ChangePasswordForm(instance=user)
    return render(request, "changepassword.html", {"form": form})


@login_required(login_url="/account/login/")
def deleteAccount(request):
    if request.method == "POST":
        username = request.user.username
        email = request.user.email
        code = gen_code()
        send_email(email, code)
        request.session["verify"] = {
            "purpose": "delete_account",
            "username": username,
            "email": email,
            "code": code,
            "expire_time": time.time() + 120,
        }
        return redirect("/account/verify_code/")
    return HttpResponseNotFound()


@login_required(login_url="/account/login/")
def statistics(request):
    if request.method == 'GET':
        user = request.user
        if request.GET.get("card_id"):
            card = get_object_or_404(BankCard, id=request.GET.get("card_id"), user=user)
        else:
            card = BankCard.objects.filter(user=user).first()
        context = draw_plot(user, card)
        context["cards"] = BankCard.objects.filter(user=user)
        return render(request, "statistics.html", context)
    

@login_required(login_url="/account/login/")
def add_card(request):
    if request.method == "POST":
        form = Card(request.POST)
        if form.is_valid():
            card_name = form.cleaned_data.get("card_name")
            card_number = form.cleaned_data.get("card_number")
            owner = form.cleaned_data.get("owner")
            BankCard.objects.create(user=request.user, card_name=card_name, card_number=card_number, owner=owner)
            return redirect("/account/profile/")
    else:
        form = Card()
    return render(request, "card.html", {"form": form, "button": "اضافه کن", "title": "اضافه کردن کارت", "info": "اضافه"})


@login_required(login_url="/account/login/")
def update_card(request, pk):
    instance = get_object_or_404(BankCard, user=request.user, id=pk)
    if request.method == "POST":
        form = Card(request.POST, instance=instance)
        if form.is_valid():
            instance.card_name = form.cleaned_data.get("card_name")
            instance.card_number = form.cleaned_data.get("card_number")
            instance.owner = form.cleaned_data.get("owner")
            instance.save()
            return redirect("/account/profile/")
    else:
        form = Card(instance=instance)
    return render(request, "card.html", {"form": form, "button": "تغییر بده", "title": "وایراش کردن کارت", "info": "ویرایش"})


login_required(login_url="/account/login/")
def delete_card(request, pk):
    if request.method == "POST":
        card = get_object_or_404(BankCard,user=request.user, id=pk)
        card.delete()
        return redirect("/account/profile/")
    else:
        return HttpResponseForbidden()