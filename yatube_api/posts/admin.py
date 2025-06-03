from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Post, Comment, Group, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "short_text", "author_link", "group_link",
        "pub_date", "image_preview", "comments_count", "likes_count"
    )
    list_display_links = ("pk", "short_text")
    search_fields = ("text", "author__username", "group__title")
    list_filter = ("pub_date", "author", "group")
    list_select_related = ("author", "group")
    readonly_fields = ("pub_date", "image_preview", "comments_count", "likes_count")
    fieldsets = (
        (None, {
            "fields": ("author", "text", "group")
        }),
        ("Медиа", {
            "fields": ("image", "image_preview"),
            "classes": ("collapse",)
        }),
        ("Статистика", {
            "fields": ("comments_count", "likes_count"),
            "classes": ("collapse",)
        }),
        ("Даты", {
            "fields": ("pub_date",),
            "classes": ("collapse",)
        }),
    )
    actions = ["clear_group"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _comments_count=Count("comments"),
            _likes_count=Count("likes")
        )

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = "Текст"

    def author_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = "Автор"
    author_link.admin_order_field = "author__username"

    def group_link(self, obj):
        if not obj.group:
            return "-"
        url = reverse("admin:posts_group_change", args=[obj.group.id])
        return format_html('<a href="{}">{}</a>', url, obj.group.title)
    group_link.short_description = "Группа"
    group_link.admin_order_field = "group__title"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Превью изображения"

    def comments_count(self, obj):
        return obj._comments_count
    comments_count.short_description = "Комментарии"
    comments_count.admin_order_field = "_comments_count"

    def likes_count(self, obj):
        return obj._likes_count
    likes_count.short_description = "Лайки"
    likes_count.admin_order_field = "_likes_count"

    def clear_group(self, request, queryset):
        updated = queryset.update(group=None)
        self.message_user(request, f"У {updated} постов удалена группа")
    clear_group.short_description = "Удалить группу у выбранных постов"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "short_text", "author_link", "post_link", "created")
    list_display_links = ("pk", "short_text")
    search_fields = ("text", "author__username", "post__text")
    list_filter = ("created", "author")
    list_select_related = ("author", "post")
    readonly_fields = ("created",)
    fieldsets = (
        (None, {
            "fields": ("post", "author", "text")
        }),
        ("Даты", {
            "fields": ("created",),
            "classes": ("collapse",)
        }),
    )

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = "Текст"

    def author_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = "Автор"
    author_link.admin_order_field = "author__username"

    def post_link(self, obj):
        url = reverse("admin:posts_post_change", args=[obj.post.id])
        return format_html('<a href="{}">Пост #{}</a>', url, obj.post.id)
    post_link.short_description = "Пост"
    post_link.admin_order_field = "post__id"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "title", "slug", "posts_count",
        "description_short", "created_date"
    )
    list_display_links = ("pk", "title")
    search_fields = ("title", "description")
    list_filter = ("created_date",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("posts_count", "created_date")
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description")
        }),
        ("Статистика", {
            "fields": ("posts_count",),
            "classes": ("collapse",)
        }),
        ("Даты", {
            "fields": ("created_date",),
            "classes": ("collapse",)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _posts_count=Count("posts")
        )

    def posts_count(self, obj):
        return obj._posts_count
    posts_count.short_description = "Посты"
    posts_count.admin_order_field = "_posts_count"

    def description_short(self, obj):
        return obj.description[:100] + "..." if obj.description else "-"
    description_short.short_description = "Описание"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user_link", "following_link", "created_at")
    list_display_links = ("pk",)
    search_fields = (
        "user__username", "user__email",
        "following__username", "following__email"
    )
    list_filter = ("created_at",)
    list_select_related = ("user", "following")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {
            "fields": ("user", "following")
        }),
        ("Даты", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "Пользователь"
    user_link.admin_order_field = "user__username"

    def following_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.following.id])
        return format_html('<a href="{}">{}</a>', url, obj.following.username)
    following_link.short_description = "Подписка"
    following_link.admin_order_field = "following__username"
