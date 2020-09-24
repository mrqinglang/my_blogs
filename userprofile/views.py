from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from userprofile.forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
# 加密
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from my_blog import settings
import random
import re
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from userprofile.forms import ProfileForm
from userprofile.models import Profile


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # cleaned_data 就是读取表单返回的值，返回类型为字典dict型
            data = user_login_form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect('article:article_list')
            else:
                return render(request, 'userprofile/login.html', {'errmsg': '账号密码不合法'})
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse('请使用GET或POST')

def user_logout(request):
    logout(request)
    return redirect('userprofile:login')

def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        pwd2 = request.POST.get('password2')
        email = request.POST.get('email')

        try:
             user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
               user = None
        if user:
            # 用户名已存在
            return render(request, 'userprofile/register.html', {'errmsg': '用户名已存在'})
        if email:
            if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return render(request, 'userprofile/register.html', {'errmsg': '请检查邮箱是否正确'})
        if pwd != pwd2:
            return render(request, 'userprofile/register.html', {'errmsg': '两次密码不一致'})
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            # 设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect('article:article_list')


    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse('请提交get或post请求')

#@login_required是一个Python装饰器。装饰器可以在不改变某个函数内容的前提下，
# 给这个函数添加一些功能。具体来说就是@login_required要求调用user_delete()函数时，
# 用户必须登录；如果未登录则不执行函数，将页面重定向到/userprofile/login/地址去。
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        if request.user == user:
            logout(request)
            user.delete()
            return redirect('userprofile:login')
        else:
            return HttpResponse('你没有删除操作的权限。')
    else:
        return HttpResponse('仅接受post请求。')


def user_reset(request):
    if request.method == 'GET':

        return render(request, 'userprofile/reset.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponse('邮箱错误')
        num = random.randint(1000, 9999)
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'num': num}
        token = serializer.dumps(info)
        token = token.decode('utf8')  # 编码里面不写默认为utf8
        # 发邮件
        subject = '密码重置'  # 标题
        message = '<h1> 您的验证码为%s<h1 />' \
                  '<a href="http://127.0.0.1:8000/userprofile/forget/%s">修改密码</a>' % (
                  num, token)
        #           'http://127.0.0.1:8000/user/registe/'  # 内容
        # sender = settings.EMAIL_BACKEND
        sender = settings.EMAIL_HOST_USER
        receiver = [email]
        send_mail(
            subject,
            '',
            sender,
            receiver,
            html_message=message)
        return redirect('userprofile:login')

    else:
        return HttpResponse('请返回get和post请求')

def user_forget(request,token):
    if request.method == 'GET':
        res = render(request, 'userprofile/forget.html')
        res.set_cookie('info', token)
        return res

def user_forget1(request):
    if request.method == 'POST':
        token = request.COOKIES.get('info')
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # print(token)
        info = serializer.loads(token)
        try:
            username = request.POST.get('username')
            pwd = request.POST.get('pwd')
            pwd1 = request.POST.get('pwd1')
            num = request.POST.get('num')
            if not all([username, pwd, pwd1, num]):
                # 数据不完整
                return render(request, 'userprofile/forget.html', {'errmsg': '数据不完整，请重新填写'})
            if num != str(info['num']):
                return render(request, 'userprofile/forget.html', {'errmsg': '验证码错误'})
            Use = User.objects.get(username=username)
            try:
                Use = User.objects.get(username=username)
            except Use.DoesNotExist:
                # 用户名不存在
                Use = None
            if  Use == None:
                # 用户名已存在
                return render(request, 'userprofile/forget.html', {'errmsg': '用户名不存在'})
            if pwd != pwd1:
                return render(request, 'userprofile/forget.html', {'errmsg': '两次密码输入不一致'})
            password = make_password(pwd)
            Use.password = password
            Use.save()
            return redirect('userprofile:login')
        except SignatureExpired as e:
            # 激活时间过期
            return render(request, 'userprofile/forget.html', {'errmsg': '激活时间已过期'})

@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    # profile = Profile.objects.get(user_id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")
        # 修改本行
        # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)
        # profile_form = ProfileForm(data=request.POST)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            # 如果 request.FILES 存在文件，则保存
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")