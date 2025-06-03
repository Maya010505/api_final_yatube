from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from posts.models import Comment, Post, Group, Follow, User
from django.shortcuts import get_object_or_404


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        allow_null=True,
        help_text="ID группы, к которой относится пост"
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "group",
            "image",
            "text",
            "pub_date",
            "likes_count",
            "comments_count",
        )
        read_only_fields = ("id", "author", "pub_date")
        extra_kwargs = {
            'text': {'trim_whitespace': False, 'min_length': 10},
            'image': {'required': False}
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_group(self, value):
        if value and not Group.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Группа не существует")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID поста, к которому относится комментарий"
    )

    class Meta:
        model = Comment
        fields = ("id", "author", "post", "text", "created")
        read_only_fields = ("id", "author", "post", "created")
        extra_kwargs = {
            'text': {'trim_whitespace': False, 'min_length': 2}
        }

    def create(self, validated_data):
        post_id = self.context['view'].kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        validated_data['post'] = post
        return super().create(validated_data)


class GroupSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "posts_count",
            "subscribers_count",
        )
        read_only_fields = ("id", "slug", "posts_count", "subscribers_count")
        extra_kwargs = {
            'title': {'min_length': 3},
            'description': {'trim_whitespace': False}
        }

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_subscribers_count(self, obj):
        return obj.followers.count()


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        help_text="Имя пользователя для подписки"
    )

    class Meta:
        model = Follow
        fields = ("id", "user", "following", "created")
        read_only_fields = ("id", "user", "created")
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message="Вы уже подписаны на этого пользователя"
            )
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError("Нельзя подписаться на самого себя")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['following'] = {
            'username': instance.following.username,
            'full_name': instance.following.get_full_name(),
            'avatar': instance.following.profile.avatar.url if hasattr(instance.following, 'profile') else None
        }
        return representation
