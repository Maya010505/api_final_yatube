from django.contrib import admin
from .models import Post, Comment, Group, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group", "image")
    list_display_links = ("pk", "text")
    search_fields = ("text", "author__username", "group__title")
    list_filter = ("pub_date", "author", "group")
    readonly_fields = ("pub_date",)
    fieldsets = (
        (None, {"fields": ("author", "text", "group")}),
        (
            "Дополнительные опции",
            {"fields": ("image", "pub_date"), "classes": ("collapse",)},
        ),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "post", "author", "text", "created")
    list_display_links = ("pk", "text")
    search_fields = ("text", "author__username", "post__text")
    list_filter = ("created", "author")
    readonly_fields = ("created",)
    fieldsets = (
        (None, {"fields": ("post", "author", "text")}),
        (
            "Дополнительные опции",
            {
                "fields": ("created",),
                "classes": ("collapse",)
            }
        ),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    list_display_links = ("pk", "title")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "following", "created_at")
    list_display_links = ("pk",)
    search_fields = ("user__username", "following__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("user", "following")}),
        ("Метаданные", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
