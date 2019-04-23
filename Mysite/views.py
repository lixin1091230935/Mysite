import datetime
from django.shortcuts import render, redirect
from blog.models import Blog
from django.db.models import Sum
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_seven_days_read_data, get_today_hot_blog, get_yesterday_hot_data
from django.core.cache import cache


def get_seven_day_hot_blog():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.\
        filter(read_details__date__lt=today, read_details__date__gte=date)\
        .values('id', 'title')\
        .annotate(read_num_sum=Sum('read_details__read_num'))\
        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    context = {}
    blog_content_type = ContentType.objects.get_for_model(Blog)  # 获取Blog类型
    date, read_nums = get_seven_days_read_data(blog_content_type)  # 通过获取的类型取得日期，阅读量
    today_hot_blogs = get_today_hot_blog(blog_content_type)
    yesterday_hot_blogs = get_yesterday_hot_data(blog_content_type)

    # 获取7天的热门博客缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    if hot_blogs_for_7_days is None:
        hot_blogs_for_7_days = get_seven_day_hot_blog()
        cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)  # 每小时刷新一次

    context['dates'] = date
    context['read_nums'] = read_nums
    context['hot_blogs'] = today_hot_blogs
    context['yesterday_hot_blogs'] = yesterday_hot_blogs
    context['seven_hot_blogs'] = hot_blogs_for_7_days
    return render(request, 'blog_home.html', context)



