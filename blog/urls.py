from django.urls import path
from .views import PostListAPIView, PostDetailAPIView , PostListView, PostDetailView

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),  # /blog/
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail")
]