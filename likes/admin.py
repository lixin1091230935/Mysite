from django.contrib import admin
from .models import LikeRecord, LikeCount


@admin.register(LikeCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('id', 'liked_num', 'content_type', 'object_id', 'content_object')


@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'liked_time', 'content_type', 'object_id', 'content_object')


