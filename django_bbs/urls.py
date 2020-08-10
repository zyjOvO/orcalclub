"""django_bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from my_bbs.views import *
from django.conf.urls.static import static

urlpatterns = [
    path('mark/',Mark.as_view()),
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-avatar/', ChangeAvatarView.as_view(), name='change-avatar'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('aboutme/', AboutMeView.as_view(), name='aboutme'),
    url(r'^$', HomeView.as_view(), name="index"),
    path('article/<int:id>/', ArticleView.as_view(), name='article'),
    path('article_dianzan', ArticleDianzanView.as_view()),
    path('article_shoucang', ArticleShoucangView.as_view()),
    path(r'post-article', PostArticleView.as_view(), name="post-article"),
    path('topic/<int:id>/', TopicView.as_view(), name='topic'),
    path('comment/<int:id>/', CommentView.as_view(), name='comment'),
    path('comment-delete/<int:id>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('newspage/', NewspageView.as_view(), name='newspage'),
    path('academic/', AcademicView.as_view(), name='academic'),
    path('tankgame/', TankgameView.as_view(), name='tankgame'),
    # url(r'^$', NewspageView.as_view(), name="newspage"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
