import json
from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown
from .models import *
from PIL import Image
from django.conf import settings


# Create your views here.
# 自定义权限认证


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginRequiredMixin(object):
    """
    登陆限定，并指定登陆url
    """

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, login_url='/login/')


# 注册模块
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get("phone")
        password = request.POST.get('password')
        user = UserProfile.objects.filter(Q(username=username) | Q(email=email))
        if user:  # 已存在邮箱或者账号
            return render(request, 'register.html', {'error': '邮箱或者账号已存在'})

        obj = UserProfile.objects.create(username=username, phone=phone, email=email)
        obj.set_password(password)
        obj.save()
        return HttpResponseRedirect(reverse('login'))


# 退出模块
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


# 登录模块
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_remember_me = request.POST.get('is_remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(0)
                if is_remember_me:
                    request.session.set_expiry(None)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"error": "用户未激活！"})
        else:
            return render(request, "login.html", {"error": "用户名或密码错误！"})


# 用户信息模块
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        topics = Topic.objects.all()
        return render(request, 'profile.html', {"user": request.user, 'topics': topics})

    def post(self, request):
        user_id = request.POST.get("id")
        interest = request.POST.get("interest")
        sex = request.POST.get("sex")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        obj = UserProfile.objects.get(id=int(user_id))
        obj.interest = interest
        obj.sex = int(sex)
        obj.address = address
        obj.phone = phone
        obj.email = email
        obj.save()
        return HttpResponseRedirect(reverse("profile"))


# 修改头像模块
class ChangeAvatarView(LoginRequiredMixin, View):

    def post(self, request):
        obj = UserProfile.objects.get(id=request.user.id)
        pic = ContentFile(request.FILES['file'].read())
        obj.image.save(request.FILES['file'].name, pic)
        obj.save()
        return HttpResponse(json.dumps({'code': 0, "avatar": obj.image.url}))


# 重置密码
class ResetPasswordView(LoginRequiredMixin, View):
    def post(self, request):
        obj = UserProfile.objects.get(id=request.user.id)
        password = request.POST.get("password")
        obj.set_password(password)
        obj.save()
        return HttpResponse(json.dumps({'code': 0, "avatar": obj.image.url}), content_type="application/json")


class HomeView(View):
    def get(self, request):
        topics = Topic.objects.all()
        articles = Article.objects.all().order_by("-publish_date")
        hot = [a for a in articles if a.comment_set.count() > 3][:6]
        paginator = Paginator(articles, 6)  # 每页显示6条数据
        page = request.GET.get('page')  # 获取请求的页数
        try:
            articles = paginator.page(page)  # 获取当前页数的数据列表
        except PageNotAnInteger:  # 如果返回的页码不是数字(空值),返回第一页
            articles = paginator.page(1)
        except EmptyPage:  # 如果页数超出范围,返回最后一页
            articles = paginator.page(paginator.num_pages)
        return render(request, "index.html", {"articles": articles, "hot": hot, "topics": topics})

    def post(self, request):
        """
        搜索逻辑
        :param request:
        :return:
        """
        q = request.POST.get("q")
        topics = Topic.objects.all()
        articles = Article.objects.filter(Q(title__contains=q) | Q(brief__contains=q) | Q(author__username__contains=q))
        hot = [a for a in articles if a.comment_set.count() > 3][:6]
        paginator = Paginator(articles, 6)  # 每页显示6条数据
        page = request.GET.get('page')  # 获取请求的页数
        try:
            articles = paginator.page(page)  # 获取当前页数的数据列表
        except PageNotAnInteger:  # 如果返回的页码不是数字(空值),返回第一页
            articles = paginator.page(1)
        except EmptyPage:  # 如果页数超出范围,返回最后一页
            articles = paginator.page(paginator.num_pages)
        return render(request, "index.html", {"articles": articles, "hot": hot, "topics": topics})


class ArticleView(View):

    def get(self, request, *args, **kwargs):
        article_id = kwargs.get("id")
        topics = Topic.objects.all()
        cur_article = list(Article.objects.filter(id=article_id).all())[0]
        tmp_next_list = list(Article.objects.filter(id__gt=article_id).values("id"))
        tmp_pre_list = list(Article.objects.filter(id__lt=article_id).values("id"))

        if len(tmp_next_list) == 0:
            nexts = list(Article.objects.filter(id=article_id).values("id"))[0]
        else:
            nexts = list(Article.objects.filter(id__gt=article_id).values("id"))[0]

        if len(tmp_pre_list) == 0:
            pres = list(Article.objects.filter(id=article_id).values("id"))[0]
        else:
            pres = list(Article.objects.filter(id__lt=article_id).values("id"))[-1]

        return render(request, "detail.html", {"article": cur_article, "topics": topics, "nexts": nexts, "pres": pres})


class ArticleDianzanView(LoginRequiredMixin, View):

    def get(self, request):
        article_id = request.GET.get("id")
        obj = Article.objects.get(id=article_id)
        obj.dianzan += 1
        obj.save()
        return HttpResponseRedirect("/")


class ArticleShoucangView(LoginRequiredMixin, View):

    def get(self, request):
        article_id = request.GET.get("id")
        obj = Article.objects.get(id=article_id)
        if ShouCang.objects.filter(user=request.user, article=obj):
            return HttpResponseRedirect("/")
        else:
            ShouCang.objects.create(user=request.user, article=obj)
            return HttpResponseRedirect("/")


class PostArticleView(LoginRequiredMixin, View):
    """
    写文章
    :param request:
    :return:
    """

    def get(self, request):
        topics = Topic.objects.all()

        return render(request, "post.html", {"topics": topics})

    def post(self, request):
        content = request.POST["content"]
        tid = request.POST["topic_id"]
        title = request.POST["title"]
        brief = request.POST["brief"]
        topic1 = Topic.objects.get(id=tid)
        article = Article.objects.create(title=title, content=content, brief=brief, topic=topic1, author=request.user)
        article.save()
        photo = request.FILES['up_image']
        if photo:
            pic = ContentFile(request.FILES['up_image'].read())
            article.image.save(request.FILES['up_image'].name, pic)
            article.save()
        return HttpResponseRedirect("/article/" + str(article.id))


class TopicView(View):
    def get(self, request, *args, **kwargs):
        topic_id = kwargs.get("id")
        topics = Topic.objects.all()
        articles = Article.objects.filter(topic_id=topic_id).all()
        paginator = Paginator(articles, 10)  # 每页显示6条数据
        page = request.GET.get('page')  # 获取请求的页数
        try:
            articles = paginator.page(page)  # 获取当前页数的数据列表
        except PageNotAnInteger:  # 如果返回的页码不是数字(空值),返回第一页
            articles = paginator.page(1)
        except EmptyPage:  # 如果页数超出范围,返回最后一页
            articles = paginator.page(paginator.num_pages)
        return render(request, "topics.html", {"articles": articles, "topics": topics, })


class CommentView(LoginRequiredMixin, View):

    def post(self, request, **kwargs):
        article_id = kwargs.get("id")
        article = Article.objects.get(id=article_id)
        content = request.POST["content"]
        Comment.objects.create(content=content, article=article, commentator=request.user)
        return HttpResponseRedirect("/article/" + str(article_id))


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        comment_id = kwargs.get("id")
        Comment.objects.get(id=comment_id).delete()
        return HttpResponse(json.dumps({'code': 0, "msg": "success"}), content_type="application/json")


class AboutMeView(LoginRequiredMixin, View):
    def get(self, request):
        topics = Topic.objects.all()
        articles = Article.objects.filter(author=request.user)
        paginator = Paginator(articles, 6)  # 每页显示6条数据
        page = request.GET.get('page')  # 获取请求的页数
        try:
            articles = paginator.page(page)  # 获取当前页数的数据列表
        except PageNotAnInteger:  # 如果返回的页码不是数字(空值),返回第一页
            articles = paginator.page(1)
        except EmptyPage:  # 如果页数超出范围,返回最后一页
            articles = paginator.page(paginator.num_pages)
        return render(request, "aboutme.html", {"articles": articles, "topics": topics})


# 导航栏资讯模块
class NewspageView(View):
    def get(self, request):
        topics = Topic.objects.all()
        return render(request, 'newspage.html', {"topics": topics})


# 导航栏学习模块
class AcademicView(View):
    def get(self, request):
        topics = Topic.objects.all()
        return render(request, 'academic.html', {"topics": topics})


# 导航栏游戏模块
class TankgameView(View):
    def get(self, request):
        return render(request, 'tankgame.html')


class Mark(View):
    def get(self, request):
        import markdown
        from django.shortcuts import render, get_object_or_404
        from .models import Article
        post = get_object_or_404(Article,pk=1)
        # 记得在顶部引入 markdown 模块
        post.content = markdown.markdown(post.content,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])

        return render(request, 'mark.html', context={'post': post})


    def post(self, request):
        return render(request, 'mark.html')
