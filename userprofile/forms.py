# --*-- coding: utf-8 --*--
# @Time     : 2020/9/19 15:40
# @Author   : mrqinglang
# @software : PyCharm
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email')
    # 对两次输入的密码是否一致进行检查
    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError('密码输入不一致,请重试。')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')


