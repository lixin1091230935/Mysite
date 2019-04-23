import random
import string
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def login(request):
    context = {}
    if request.method == 'POST':  # 提交数据
        login_form = LoginForm(request.POST)  # 获取数据
        if login_form.is_valid():  # 是否有效
            user = login_form.cleaned_data['user']  # cleaned_data类型是字典，里面是提交成功后的信息
            auth.login(request, user)
            return redirect(request.GET.get('form', reverse('home')))  # 返回到之前的页面
    else:
        login_form = LoginForm()  # 实例化
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def register(request):
    context = {}
    if request.method == "POST":
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session
            del request.session['register_code']
            # 在创建之后登陆
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)


# 注销登陆
def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


# 用户信息
def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)


# 修改昵称
def change_nickname(request):
    Redirect = redirect(request.GET.get('from', reverse('home')))
    context = {}
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, create = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return Redirect
    else:
        form = ChangeNicknameForm()

    context['page_title'] = "修改昵称"
    context['submit_title'] = "确定"
    context['form_title'] = "修改昵称"
    context['form'] = form
    context['return_back_url'] = Redirect
    return render(request, 'form.html', context)


# 绑定邮箱,此功能主要适用于第3方登陆，并不适合直接登陆注册的用户
def bind_email(request):
    context = {}
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        # 在BindEmailForm中也需要使用request
        form = BindEmailForm(request.POST, request=request)

        # form表单验证有效 开始绑定邮箱
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_title'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'bind_email.html', context)


# 发送验证码
def send_verification_code(request):
    data = {}
    email = request.GET.get("email", "")  # 通过ajax提交的数据获取email
    send_for = request.GET.get("send_for", "")  #
    if email != "":
        # 生成验证码
        verification_code = "".join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        # 保存session
        else:
            request.session[send_for] = verification_code
            request.session['send_code_time'] = now

            # 发送邮件以及其基本格式
            send_mail(
                "绑定邮箱",
                verification_code,
                "1091230935@qq.com",
                [email],
                fail_silently=False,
            )
            data['status'] = "SECCESS"
    else:
        data['status'] = "ERROR"
    return JsonResponse(data)


# 修改密码
def change_password(request):
    context = {}
    # 修改密码后需要回到主界面
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context['page_title'] = "修改密码"
    context['submit_title'] = "确定"
    context['form_title'] = "修改密码"
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)


def forgot_password(request):
    context = {}
    redirect_to = reverse('home')  # 修改完密码回到首页
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password_again']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_title'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'forgot_password.html', context)




