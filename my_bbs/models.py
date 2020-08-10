from django.db import models
from tinymce.models import HTMLField
# Create your models here.

from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    '''扩展Django自带的User模型'''
    nickname = models.CharField("用户昵称", max_length=64, null=True)
    sex = models.IntegerField(verbose_name="性别", choices=((0, '男'), (1, '女')), default=0)
    phone = models.CharField(verbose_name="手机号", null=True, max_length=11)
    address = models.CharField(verbose_name="手机号", null=True, max_length=255)
    interest = models.CharField(max_length=255, null=True, verbose_name="兴趣")
    image = models.ImageField(max_length=1000, upload_to='upload', verbose_name=u'头像', blank=True,
                              default='upload/default.jpg')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name


class Topic(models.Model):
    '''
    话题信息
    '''
    topic = models.CharField("话题名称", max_length=16)
    parent_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.topic

    class Meta:
        verbose_name = "话题"
        verbose_name_plural = verbose_name


class Article(models.Model):
    title = models.CharField("标题", max_length=128)
    brief = models.CharField("简介", max_length=512)
    content = HTMLField(verbose_name='文章详情')
    author = models.ForeignKey(UserProfile, verbose_name="作者", on_delete=models.CASCADE)
    image = models.ImageField("图片", upload_to="upload", default="upload/21.jpg")
    video = models.FileField("视频", upload_to="upload", default="upload/logo2_03.png", null=True)
    dianzan = models.IntegerField("点赞", default=0)
    topic = models.ForeignKey(Topic, verbose_name="所属话题", on_delete=models.CASCADE)
    publish_date = models.DateTimeField("发布时间", auto_now_add=True, editable=True)
    update_date = models.DateTimeField("更新时间", auto_now=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['publish_date']
        verbose_name = "文章"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    '''
    评论的数据模型
    '''
    article = models.ForeignKey(Article, verbose_name="所属文章", on_delete=models.CASCADE)
    commentator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    comment_date = models.DateTimeField("评论时间", auto_now_add=True, editable=True)
    parent_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['comment_date']
        verbose_name = "评论"
        verbose_name_plural = verbose_name


class ShouCang(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="所属文章")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='shoucang')
    create_time = models.DateTimeField("收藏时间", auto_now_add=True, editable=True)

    class Meta:
        ordering = ['create_time']
        verbose_name = "收藏"
        verbose_name_plural = verbose_name