from django import template
from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.models import ContentType
from ..views import LikeCount, LikeRecord

register = template.Library()


@register.simple_tag()
def get_like_count(obj):  # 获取点赞数量，可能是博客点赞或者评论点赞
    content_type = ContentType.objects.get_for_model(obj)  # 内容的类型
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
    return like_count.liked_num


@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    if not user.is_authenticated:
        return ''
    if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=context['user']).exists():
        return 'active'
    else:
        return ''


@register.simple_tag()
def get_content_type(obj):
    # 传入实例化对象获取它的模型类型
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.model
