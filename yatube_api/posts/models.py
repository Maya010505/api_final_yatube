from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.urls import reverse

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название группы",
        help_text="Максимальная длина 200 символов",
        validators=[
            MinLengthValidator(
                3,
                message="Название группы должно содержать минимум 3 символа"
            )
        ]
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный идентификатор",
        help_text="Максимальная длина 50 символов. Только буквы, цифры, дефисы и подчёркивания",
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message="Можно использовать только латинские буквы, цифры, дефисы и подчёркивания"
            )
        ]
    )
    description = models.TextField(
        verbose_name="Описание группы",
        help_text="Подробное описание сообщества",
        blank=True
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_groups",
        verbose_name="Администратор группы"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("group_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"
        ordering = ["-created_date"]


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Напишите что-нибудь интересное",
        validators=[
            MinLengthValidator(
                10,
                message="Пост должен содержать минимум 10 символов"
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор"
    )
    image = models.ImageField(
        upload_to="posts/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name="Изображение",
        help_text="Можно загрузить изображение"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Сообщество",
        help_text="Выберите сообщество (необязательно)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения"
    )

    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]
        indexes = [
            models.Index(fields=["pub_date", "author"]),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост"
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Напишите ваш комментарий",
        validators=[
            MinLengthValidator(
                2,
                message="Комментарий должен содержать минимум 2 символа"
            )
        ]
    )
    created = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        db_index=True
    )
    updated = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name="Редактировался"
    )

    def save(self, *args, **kwargs):
        if self.pk:  # Если комментарий уже существует
            self.is_edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Комментарий {self.author} к посту {self.post.id}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["post", "created"]),
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки",
        db_index=True
    )
    notify = models.BooleanField(
        default=True,
        verbose_name="Уведомления",
        help_text="Получать уведомления о новых постах"
    )

    def clean(self):
        if self.user == self.following:
            raise models.ValidationError(
                {"following": "Нельзя подписаться на самого себя"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} подписан на {self.following}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"],
                name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="prevent_self_follow"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["-created_at"]
