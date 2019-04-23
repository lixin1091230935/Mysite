from django.urls import path
from . import views

# 开始于127.0.0.1:8000/blog
urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('<int:art_id>', views.blog_detail, name='blog_detail'),
    path('type/<int:blog_type_pk>', views.blogs_with_type, name='blogs_with_type'),
    path('date/<int:year>/<int:month>', views.blogs_with_date, name='blogs_with_date')
]