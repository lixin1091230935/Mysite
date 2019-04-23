from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import Comment_forms


register = template.Library()


@register.simple_tag()
def get_comment_count(obj):
    content_ype = ContentType.objects.get_for_model(obj)
    count = Comment.objects.filter(content_type=content_ype, object_id=obj.pk).count()
    return count


@register.simple_tag()
def get_comment_form(obj):
    content_ype = ContentType.objects.get_for_model(obj)
    # 初始化comment表单 并且传入type and blog_id
    form = Comment_forms(initial={'content_type': content_ype.model,
                                  'object_id': obj.pk,
                                  'reply_comment_id': '0'})
    return form


@register.simple_tag()
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None).order_by('-comment_time')

    return comments