import datetime
from django.db.models import Sum  # 聚合函数
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.utils import timezone


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    # get_or_create是更为快捷的方式（有两个返回值）
    # readnum, create = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
    if not request.COOKIES.get(key):
        # 总阅读数加一
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数 +1
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key


def get_seven_days_read_data(content_type):  # 七天的阅读数统计，传入
    today = timezone.now().date()  # 今天时间
    dates = []
    read_nums = []
    for i in range(7, 0, -1):  # 获取前七天的阅读数
        date = today - datetime.timedelta(days=i)  # 得到日期
        dates.append(date.strftime('%m%d'))  # 保存一下日期
        # 从指定的日期获取阅读量，一般都会有多条数据（同一天阅读不同的博客会有不同的记录）
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))  # 通过聚合函数对同一天阅读量进行求和
        read_nums.append(result['read_num_sum'] or 0)   #
    return dates, read_nums


def get_today_hot_blog(content_type):  # 获取当天的热门博客
    today = timezone.now().date()
    # 通过今天的日期筛选博客并且使用order_by排序
    read_retail = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_retail[:7]  # 取热门的前7条博客


def get_yesterday_hot_data(content_type):  # 获取昨天的热门博客
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    # 通过昨天的日期筛选博客并且使用order_by排序
    read_retail = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_retail[:7]  # 取热门的前7条博客

