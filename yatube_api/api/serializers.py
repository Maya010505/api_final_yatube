from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from posts.models import Comment, Post, Group, Follow


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False, allow_null=True
    )

    class Meta:
        fields = (
            "author",
            "group",
            "id",
            "image",
            "text",
            "pub_date",
        )
        read_only_fields = ("id", "author")
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )

    class Meta:
        fields = ("id", "author", "post", "text", "created")
        read_only_fields = ("id", "author", "post", "created")
        model = Comment


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            "description",
            "id",
            "slug",
            "title",
        )
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    following = serializers.StringRelatedField()

    class Meta:
        model = Follow
        fields = ("user", "following")
        read_only_fields = ("id", "user", "following")
