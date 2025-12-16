# -*- coding: utf-8 -*-

from django import forms
from .models import User

class RegisterForm(forms.Form):

    username = forms.CharField(max_length=50, label='نام کاربری',widget=forms.TextInput(attrs={"class":'form-control', "placeholder":"نام کاربری دلخواه خود را وارد"}))
    email = forms.EmailField(max_length=150, label='ایمیل', widget=forms.EmailInput(attrs={"class":"form-control", "placeholder":"ایمیل خود را وارد کنید"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class":'form-control', 'placeholder':"رمز عبور خود را وارد کنید"}), label='رمزعبور', )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", 'placeholder':"دوباره رمز عبور خود را وارد کنید"}), label='دوباره رمز عبور')

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Password's are not match!!")
    

    def save(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password1")
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
    

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label='نام کاربری',widget=forms.TextInput(attrs={"class":'form-control', "placeholder":"نام کاربری خود را وارد کنید"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":'form-control', 'placeholder':"رمز عبور خود را وارد کنید"}), label='رمزعبور', )
