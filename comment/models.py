import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render


class SendMail(threading.Thread):
    def __init__(self, subject, text, email):
        self.subject = subject
        self.text = text
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        # 发送邮件通知
        send_mail(self.subject,
                  '',
                  settings.EMAIL_HOST_USER,
                  [self.email],
                  fail_silently=False,
                  html_message=self.text
                  )


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    comment_context = models.TextField()  # 评论内容 不限字数
    comment_time = models.DateTimeField(auto_now_add=True)  # 评论时间，自动添加时间

    # 用自定义的方式定义主表的外键，而related_name就实现这个功能，在子表中定义外键时，增加related_name字段指定这个子表在主表中对应的外键属性
    comment_user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)  # 评论者

    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    # 回复即可看成是对评论进行评论
    # user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)  # 父评论
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def send_mail(self):
        context = {}
        if self.parent is None:
            subject = "有人评论了你的博客"
            # email 发送给 博客作者
            email = self.content_object.get_email()
        else:
            subject = "有人回复了你的评论"
            # email 发送给 评论的人
            email = self.reply_to.email
        if email != "":
            # text 发送内容
            context['comment_context'] = self.comment_context
            text = render(None, 'send_mail.html', context).content.decode('utf-8')
            context['url'] = self.comment_context + self.content_object.get_url()
            send_mail = SendMail(subject, text, email)

        send_mail.start()

    def __str__(self):
        return self.comment_context

    class Meta:
        ordering = ['comment_time']




