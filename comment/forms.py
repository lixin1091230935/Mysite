from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment


class Comment_forms(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)  # 字段隐藏不显示
    object_id = forms.IntegerField(widget=forms.HiddenInput)  # 字段隐藏不显示

    # 评论内容
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'))
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': "reply_comment_id"}))

    def __init__(self, *args, **kwargs):
        # 列表的get方法：如果存在这个参数则返回，不存在则返回none
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(Comment_forms, self).__init__(*args, **kwargs)

    # 用户是否登陆，评论不能为空验证
    def clean(self):
        # 判断用户时候否登陆
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("用户尚未登陆")

        # 获取评论类型是评论博客还是回复评论
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(pk=object_id)
            # 保存类型
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论不存在对象不存在')
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')
        return reply_comment_id

