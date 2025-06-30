from django.urls import path
from .views import PostListAPIView, PostDetailAPIView , PostListView, PostDetailView

urlpatterns = [
    path('api/posts/', PostListAPIView.as_view(), name='post-list'),
    path('api/posts/<slug:slug>/', PostDetailAPIView.as_view(), name='post-detail'),
    path("", PostListView.as_view(), name="post-list"),  # /blog/
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail")
]