from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator  # 导入分页器
from .models import Blog, Blogtype
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read
from user.forms import LoginForm


def public(request, blog_all_list):
    context ={}
    page_num = request.GET.get('page', 1)  # 获取url的页面参数例如：www.blog/?page=1
    paginator = Paginator(blog_all_list, 5)  # 对所有博客 每十篇博客进行分页
    page_of_blogs = paginator.get_page(page_num)  # 获取具体那一页的博客
    # 显示正确有效的页码，获取当前页码前后各两页
    # paginator.num_pages是获取分页器的总页码
    page_range = [x for x in range(int(page_num) - 2, int(page_num) + 3) if 0 < x <= paginator.num_pages]
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # # 获取分类博客数量
    blog_type_count = Blogtype.objects.annotate(blog_count=Count('blog'))

    # 获取归档日期对应的博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    context['blogs'] = page_of_blogs.object_list  # 这种方式可以获取此页的所有博客
    context['page_range'] = page_range
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = Blogtype.objects.annotate(blog_count=Count('blog'))
    context['blogs_date'] = blog_dates_dict
    return context


def blog_detail(request, art_id):  # 博客id
    context = {}
    try:
        blog = get_object_or_404(Blog, pk=art_id)
        read_cookie_key = read_statistics_once_read(request, blog)
    except Blog.DoesNotExist:
        raise Http404('not exist')
    context['next_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()  # 下一篇博客，通过创建时间而排序的
    context['previous_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()    # 上一篇博客
    context['blog'] = blog
    context['login_form'] = LoginForm()
    response = render(request, 'blog_detail.html', context)  # 返回响应
    response.set_cookie(read_cookie_key, 'true')   # 设置cookie
    return response


def blog_list(request):
    blog_all_list = Blog.objects.all()  # 获取所有博客
    context = public(request, blog_all_list)
    return render(request, 'blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(Blogtype, pk=blog_type_pk)  # 找到博客类型
    blog_all_list = Blog.objects.filter(blog_type=blog_type)  # 筛选出这个博客类型的所有博客
    context = public(request, blog_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blog_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)  # 筛选出时间段的博客
    context = public(request, blog_all_list)
    return render(request, 'blogs_with_date.html', context)
