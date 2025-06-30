from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Post
from .serializers import PostSerializer
from django.views import View


class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    
class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    
    
class PostListView(View):
    def get(self, request):
        return render(request, "blog/post_list.html")

class PostDetailView(View):
    def get(self, request, slug):
        return render(request, "blog/post_detail.html", {"slug": slug})