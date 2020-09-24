# --*-- coding: utf-8 --*--
# @Time     : 2020/9/19 9:46
# @Author   : mrqinglang
# @software : PyCharm
from django import forms
from article.models import ArticlePost

# class ArticlePostForm(forms.ModelForm):
#     class Meta:
#         model = ArticlePost
#         fields = ('title', 'body')
# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'id', 'avatar')