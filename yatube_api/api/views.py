from rest_framework import viewsets, permissions, mixins, status, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound

from posts.models import Post, Comment, Group, Follow, User
from .permissions import OwnerOrReadOnly
from .serializers import (
    PostSerializer,
    CommentSerializer,
    GroupSerializer,
    FollowSerializer,
)
from .throttling import WorkingHoursRateThrottle


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый ViewSet с возможностью создания, получения списка и отдельного элемента
    """
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    pagination_class = LimitOffsetPagination
    permission_classes = (OwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'text')
    ordering_fields = ('pub_date', 'author')
    ordering = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            raise ValidationError({'detail': 'Вы уже лайкнули этот пост'})
        post.likes.add(user)
        return Response({'status': 'Лайк добавлен'}, status=status.HTTP_200_OK)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (OwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs.get("post_id")
        ).select_related('author', 'post')

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
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'description')


class FollowViewSet(CreateListRetrieveViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("following__username", "user__username")
    throttle_classes = (ScopedRateThrottle,)

    def get_queryset(self):
        return Follow.objects.filter(
            user=self.request.user
        ).select_related('following')

    def create(self, request, *args, **kwargs):
        """Создание новой подписки с улучшенной валидацией"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        following_username = serializer.validated_data.get('following')
        following_user = get_object_or_404(User, username=following_username)

        if request.user == following_user:
            raise ValidationError(
                {'following': 'Нельзя подписаться на самого себя'},
                code=status.HTTP_400_BAD_REQUEST
            )

        if Follow.objects.filter(
                user=request.user,
                following=following_user
        ).exists():
            raise ValidationError(
                {'following': 'Вы уже подписаны на этого пользователя'},
                code=status.HTTP_400_BAD_REQUEST
            )

        follow = serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Получение списка подписчиков текущего пользователя"""
        followers = Follow.objects.filter(
            following=request.user
        ).select_related('user')
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)