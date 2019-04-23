from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from read_statistics.models import ReadNum, Get_read_num_Method
from django.contrib.contenttypes.fields import GenericRelation
from read_statistics.models import ReadDetail
from django.urls import reverse

class Blogtype(models.Model):
    type_name = models.CharField(max_length=20)

    def __str__(self):
        return self.type_name


class Blog(models.Model, Get_read_num_Method):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(Blogtype, on_delete=models.CASCADE, default='1')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    content = RichTextUploadingField()
    read_details = GenericRelation(ReadDetail)
    create_time = models.DateTimeField(auto_now_add=True)    # 自动设置创建时间
    last_updated_time = models.DateTimeField(auto_now=True)    # 自动更新现在的时间

    def __str__(self):
        return "<Blog: %s>" % self.title

    class Meta:
        ordering = ['-create_time']

    def get_url(self):
        return reverse('blog_detail', kwargs={'art_id': self.pk})

    def get_email(self):
        return self.author.email


