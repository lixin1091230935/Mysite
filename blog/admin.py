from django.contrib import admin
from .models import Blogtype, Blog

# Register your models here.注册你的模型
@admin.register(Blogtype)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_read_num', 'blog_type', 'content', 'create_time', 'last_updated_time')

# admin.site.register(art, artAdmin)    # 注册模型 现在不用这种写法，可以使用装饰器
