from django import forms
from .models import User, Expense, Income
from django.contrib.auth.hashers import check_password
import time


class RegisterForm(forms.Form):

    username = forms.CharField(max_length=50, label='نام کاربری',widget=forms.TextInput(attrs={"class":'form-control', "placeholder":"نام کاربری دلخواه خود را وارد"}))
    email = forms.EmailField(max_length=150, label='ایمیل', widget=forms.EmailInput(attrs={"class":"form-control", "placeholder":"ایمیل خود را وارد کنید"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class":'form-control', 'placeholder':"رمز عبور خود را وارد کنید"}), label='رمزعبور', )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", 'placeholder':"دوباره رمز عبور خود را وارد کنید"}), label='دوباره رمز عبور')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("پسورد های یکی نیستند")
        return cleaned_data
        

    def clean_email(self):
        super().clean()
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("این ایمیل قبلا ثبت شده")
        return email
    

    def save(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password1")
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
    

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label='نام کاربری',widget=forms.TextInput(attrs={"class":'form-control', "placeholder":"نام کاربری خود را وارد کنید"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":'form-control', 'placeholder':"رمز عبور خود را وارد کنید"}), label='رمزعبور', )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        user = User.objects.filter(username__iexact = username)
        if not user:
            raise forms.ValidationError("نام کاربری وجود نداره اگه حساب نداری یکی بساز.")
        password = cleaned_data.get("password")
        result = User.objects.get(username__iexact=username).check_password(password)
        if not result:
            raise forms.ValidationError("نام کاربری یا پسورد اشتباه است.")
        return cleaned_data


class ExpenseIncomeForm(forms.ModelForm):
    # title = forms.CharField(max_length=50, label="عنوان",widget=forms.TextInput(attrs={"class": 'form-control', 'placeholder': "عنوان مورد نظر خود را وارد کنید"}))
    # text = forms.CharField(label="توضیحات",required=False ,widget=forms.Textarea(attrs={"placeholder": "توضیحات مربوط به عنوان خود را وارد کنید (اجباری نیست)", 'class': 'form-control', "rows":1}))
    # amount = forms.IntegerField(label="مبلغ", widget=forms.NumberInput(attrs={"class": "form-control", 'placeholder': "مبلغ را وارد کنید"}))
    # date = forms.DateField(label="تاریخ", initial=today, widget=forms.DateInput(attrs={"class":'form-control', 'placeholder': "تاریخ مورد نظر را وارد کنید(پیشفرض امروز در نظر گرفته میشود)(میلادی وارد شود!!)"}))
    # time = forms.TimeField(label="زمان", initial=now, required=False,widget=forms.TimeInput(attrs={"class": "form-control", 'placeholder': "زمان مورد نظر خود را وارد کنید(پیشفرض زمان حال در نظر گرفته میشود)"}))

    # def clean_amount(self):
    #     super().clean()
    #     amount = self.cleaned_data.get("amount")
    #     if amount <= 0:
    #         raise forms.ValidationError("مبلغ باید عددی مثبت و غیر صفر باشد!")
    #     return amount
    # date = forms.DateField(label="تاریخ", widget=forms.DateInput(attrs={"class":'form-control', 'placeholder': "تاریخ مورد نظر را وارد کنید(پیشفرض امروز در نظر گرفته میشود)(میلادی وارد شود!!)"}))
    # time = forms.TimeField(label="زمان", required=False,widget=forms.TimeInput(attrs={"class": "form-control", 'placeholder': "زمان مورد نظر خود را وارد کنید(پیشفرض زمان حال در نظر گرفته میشود)"}))
    
    text = forms.CharField(label="توضیحات",required=False ,widget=forms.Textarea(attrs={"placeholder": "توضیحات مربوط به عنوان خود را وارد کنید (اجباری نیست)", 'class': 'form-control', "rows":1}))
    class Meta:
        model = Income
        fields = ("title", "text", "amount", "date", "time")
        labels = {"title":"عنوان", "text":"توضیحات", "amount":"مبلغ", "date":"تاریخ", "time":"زمان"}
        error_messages = {
            "date": {"invalid": "تاریخ باید به فرمت (روز-ماه-سال) باشد"}
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": 'form-control', 'placeholder': "عنوان مورد نظر خود را وارد کنید"}),
            "text": forms.Textarea(attrs={"placeholder": "توضیحات مربوط به عنوان خود را وارد کنید (اجباری نیست)", 'class': 'form-control', "rows":1}),
            "amount": forms.NumberInput(attrs={"class": "form-control", 'placeholder': "مبلغ را وارد کنید"}),
            "date": forms.DateInput(attrs={"class":'form-control', 'placeholder': "تاریخ مورد نظر را وارد کنید(پیشفرض امروز در نظر گرفته میشود)(میلادی وارد شود!!)"}),
            "time": forms.TimeInput(attrs={"class": "form-control", 'placeholder': "زمان مورد نظر خود را وارد کنید(پیشفرض زمان حال در نظر گرفته میشود)"})
        }

    def clean_amount(self):
        super().clean()
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("مبلغ باید عددی مثبت و غیر صفر باشد!")
        return amount


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, label="نام", widget=forms.TextInput(attrs={"class":'form-control', 'placeholder': 'نام خود را وارد کنید.'}))
    last_name = forms.CharField(max_length=50, required=False, label="نام خانوادگی", widget=forms.TextInput(attrs={"class":'form-control', 'placeholder': 'نام خانوادگی خود را وارد کنید.'}))
    username = forms.CharField(max_length=50, required=True, label="نام کاربری", widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "نام کاربری خود را وارد کنید."}))
    email = forms.EmailField(max_length=150, required=True, label="ایمیل",widget=forms.EmailInput(attrs={"class":'form-control', "placeholder": "ایمیل خود را وارد کنید"}))
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        else:
            if user.username == self.instance.username:
                return username
            raise forms.ValidationError("این نام کاربری مطعلق به شخص دیگریست")


class ChangePasswordForm(forms.ModelForm):
    current_password = forms.CharField(label="پسورد فعلی", widget=forms.PasswordInput(attrs={"class":"form-control"}))
    p1 = forms.CharField(label='رمز عبور جدید', widget=forms.PasswordInput(attrs={"class":"form-control"}))
    p2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput(attrs={"class":"form-control"}))

    class Meta:
        model = User
        fields = []
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("p1")
        p2 = cleaned_data.get("p2")
        current_password = cleaned_data.get("current_password")

        if not self.instance.check_password(current_password):
            raise forms.ValidationError("پسورد اشتباه است دوباره امتحان کنید")
        if not p1 == p2:
            raise forms.ValidationError("پسورد های جدید باهم یکی نیستند.")
        return cleaned_data
    

class VerifyCodeForm(forms.Form):
    code = forms.CharField(label="کد تایید", widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"کد تایید ارسال شده به ایمیل خود را وارد کنید."}))

    def __init__(self, *args, verify_code=None, expire_time=None,**kwargs):
        super().__init__(*args, **kwargs)
        self.verify_code = verify_code
        self.expire_time = expire_time

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if time.time() > self.expire_time:
            raise forms.ValidationError("کد شما منقضی شده لطفا کد جدید را وارد کنید")
        elif not code == self.verify_code:
            raise forms.ValidationError("کد وارد شده اشتباه است.")
        return code