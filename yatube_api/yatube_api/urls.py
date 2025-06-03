from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from api.views import PostViewSet, CommentsViewSet, GroupViewSet, FollowViewSet

router = routers.DefaultRouter()
router.register(r"posts", PostViewSet)
router.register(
    r"posts/(?P<post_id>\d+)/comments", CommentsViewSet, basename="comments"
)
router.register(r"groups", GroupViewSet)
router.register(r"follow", FollowViewSet, basename="follow")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path(
        "redoc/",
        TemplateView.as_view(template_name="redoc.html"),
        name="redoc"
    ),
    path("api/v1/", include("djoser.urls")),
    path("api/v1/", include("djoser.urls.jwt")),
]
