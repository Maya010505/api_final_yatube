from rest_framework import viewsets, permissions, mixins, status, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from posts.models import Post, Comment, Group, Follow, User
from .permissions import OwnerOrReadOnly
from .serializers import (
    PostSerializer,
    CommentSerializer,
    GroupSerializer,
    FollowSerializer,
)
from .throttling import WorkingHoursRateThrottle


class CreateQueryViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    pagination_class = LimitOffsetPagination
    permission_classes = (OwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # pagination_class = CommentPagination
    permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs.get("post_id"))

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if "post_id" in kwargs:
            get_object_or_404(Post, id=kwargs["post_id"])


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny,)


class FollowViewSet(CreateQueryViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("following__username",)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Создание новой подписки"""
        following_username = request.data.get("following")
        if not following_username:
            return Response(
                {"error": "Не указан пользователь для подписки"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            following_user = User.objects.get(username=following_username)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user == following_user:
            return Response(
                {"error": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(
            user=request.user,
            following=following_user
        ).exists():
            return Response(
                {"error": "Вы уже подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(
            user=request.user,
            following=following_user
        )
        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
