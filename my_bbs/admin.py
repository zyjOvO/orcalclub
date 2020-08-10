from django.contrib import admin
from .models import *


class UserProfileAdmin(admin.AdminSite):
    list_display = ('username', 'email', 'phone', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone',)
    list_filter = ('date_joined',)


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "publish_date", "topic", "image")
    search_fields = ("title",)


class TopicsAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "parent_id")


class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "commentator", "comment_date", "parent_id")


admin.site.register(UserProfile)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(Comment, CommentsAdmin)
admin.site.register(Topic, TopicsAdmin)

