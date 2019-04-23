from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


# 登陆时验证
class LoginForm(forms.Form):
    # 定制form表单
    username_or_email = forms.CharField(label="用户名或邮箱",
                               widget=forms.TextInput(
                                attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}))
    password = forms.CharField(label="密码",
                               widget=forms.PasswordInput(
                                attrs={'class': 'form-control', 'placeholder': "请输入密码"}))  # 密码设置密文

    # 用户名密码是否正确可以放入form中验证
    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        # 认证给出的用户名和密码，使用authenticate()函数。它接受两个参数，用户名username和密码password
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:  # 抛出错误信息
            if User.objects.filter(email=username_or_email).exists():
                # 通过绑定的邮箱获取username并判断
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('账号或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


# 注册时验证
class RegForm(forms.Form):
    # 定制form表单
    username = forms.CharField(label="用户名",
                               max_length=30,
                               min_length=3,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入3-30位的用户名'}))
    password = forms.CharField(label="密码",
                               min_length=6,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': "请输入密码"}))  # 密码设置密文
    password_again = forms.CharField(label="再次输入密码",
                                     min_length=6,
                                     widget=forms.PasswordInput(
                                        attrs={'class': 'form-control', 'placeholder': "请输入密码"}))  # 密码设置密文
    email = forms.CharField(label="邮箱",
                            widget=forms.EmailInput(
                                   attrs={'class': 'form-control', 'placeholder': "请输入邮箱"}))  # 密码设置密文
    verification_code = forms.CharField(label="验证码",
                                        required=False,  # 此字段不非必填字段
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"至邮箱'}))

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', "")
        # code是后台生成的验证码
        # verification_code是通过form表单获取的用户输入的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError("两次密码不一样")
        return password_again

    # 验证邮箱是否已经被注册了
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱已存在")
        return email


# 修改昵称验证
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label="新的昵称",
                                   max_length=30,
                                   widget=forms.TextInput(
                                     attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))

    def __init__(self, *args, **kwargs):
        # 列表的get方法：如果存在这个参数则返回，不存在则返回none
        # 获取
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    # 用户是否登陆，
    def clean(self):
        # 判断用户时候否登陆
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("用户尚未登陆")
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get("nickname_new", "").strip()
        if nickname_new == "":
            raise forms.ValidationError("新的昵称不能为空")
        else:
            return nickname_new


# 绑定短信
class BindEmailForm(forms.Form):
    email = forms.EmailField(label="邮箱",
                             max_length=30,
                             widget=forms.EmailInput(
                                attrs={'class': 'form-control', 'placeholder': '请输入正确邮箱'}))

    # 验证码
    verification_code = forms.CharField(label="验证码",
                                        required=False,  # 此字段不非必填字段
                                        widget=forms.TextInput(
                                           attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"至邮箱'}))

    def __init__(self, *args, **kwargs):
        # 列表的get方法：如果存在这个参数则返回，不存在则返回none
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    # 用户是否登陆等等
    def clean(self):
        # 判断用户时候否登陆
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError("用户尚未登陆！！！")

        # 判断用户是否绑定邮箱
        if self.request.user.email != "":
            raise forms.ValidationError("你已经绑定邮箱了！！！")

        # 判断验证码:  获取用户输入的验证码 + 对比验证码是否正确
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', "")
        # code是后台生成的验证码
        # verification_code是通过form表单获取的用户输入的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("改邮箱已经绑定")
        return email

    # def clean_verification_code(self):
    #     verification_code = self.cleaned_data.get('verification_code', "").strip()
    #     if verification_code == "":
    #         raise forms.ValidationError("验证码不能为空")
    #     return verification_code


# 修改密码
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="旧密码",
                                   widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': "请输入旧密码"}))  # 密码设置密文
    new_password = forms.CharField(label="新密码",
                                   widget=forms.PasswordInput(
                                        attrs={'class': 'form-control', 'placeholder': "请输入新密码"}))  # 密码设置密文
    new_password_again = forms.CharField(label="再次输入新密码",
                                         widget=forms.PasswordInput(
                                            attrs={'class': 'form-control', 'placeholder': "再次输入新密码"}))  # 密码设置密文

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    # 验证两次面膜是否一致
    def clean(self):
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    # 验证旧密码是否正确
    def clean_old_password(self):
        # 从form中获取输入的旧密码
        old_password = self.cleaned_data.get("old_password", "")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("旧的密码输入错误")
        return old_password


# 忘记密码 通过发送验证码重置密码
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="您的邮箱/Email",
                             required=False,
                             widget=forms.EmailInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入3-30位的用户名'}))

    new_password = forms.CharField(label="新密码",
                                   required=False,
                                   widget=forms.PasswordInput(
                                     attrs={'class': 'form-control', 'placeholder': "请输入旧密码"}))  # 密码设置密文
    new_password_again = forms.CharField(label="再次输入新密码",
                                         required=False,
                                         widget=forms.PasswordInput(
                                            attrs={'class': 'form-control', 'placeholder': "请输入旧密码"}))  # 密码设置密文
    verification_code = forms.CharField(label="验证码",
                                        required=False,  # 此字段不非必填字段
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"至邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    # 验证两次密码是否一致
    def clean_new_password_again(self):
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return new_password_again

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    def clean_verification_code(self):
        # 获取验证码
        verification_code = self.cleaned_data['verification_code']
        if verification_code == "":
            raise forms.ValidationError("验证码不能为空")

        # 对比验证码是否正确
        code = self.request.session.get("forgot_password_code", "")
        if not (code == verification_code and code != ""):
            raise forms.ValidationError("验证码不正确")
        return verification_code
