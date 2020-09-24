# --*-- coding: utf-8 --*--
# @Time     : 2020/9/20 21:16
# @Author   : mrqinglang
# @software : PyCharm
from django import forms
from comment.models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']