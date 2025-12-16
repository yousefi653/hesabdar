from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from json import JSONEncoder
from .models import User
from .forms import RegisterForm, LoginForm

# Create your views here.
def login_first(request):
    return JsonResponse({'status': 'Login first.'})


@csrf_exempt
def register(request):
    if request.method == "GET":
            form = RegisterForm()
            return render(request, 'register.html', context={'form':form})
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status":'you are successfuly registered'}, encoder=JSONEncoder)


@csrf_exempt
def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', context={"form": form})
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user:
                dj_login(request, user=user)
                return JsonResponse({"status":"successfuly logined..","logined":request.user.is_authenticated})
        return JsonResponse({"status":f"Not found", "error":"username or password is incorrect"}, encoder=JSONEncoder)
    

@csrf_exempt
@login_required(login_url='/login-first/')
def logout(request):
    if request.method == "POST":
        dj_logout(request)
        return JsonResponse({'status': 'logout successfuly', "login": request.user.is_authenticated}, encoder=JSONEncoder)
    

