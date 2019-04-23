from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Comment
from .forms import Comment_forms
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings


# 更新评论
def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = Comment_forms(request.POST, user=request.user)
    data = {}

    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.comment_user = comment_form.cleaned_data['user']
        comment.comment_context = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.comment_user
        comment.save()

        # 通过邮件发送通知
        comment.send_mail()

        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.comment_user.get_nickname_or_username()
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.comment_context
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
