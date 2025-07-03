from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Post
from .serializers import PostSerializer
from django.views import View
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    
class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    
@method_decorator(cache_page(15), name='dispatch')
class PostListView(View):
    def get(self, request):
        return render(request, "blog/post_list.html")

@method_decorator(cache_page(60 * 5), name='dispatch')
class PostDetailView(View):
    def get(self, request, slug):
        return render(request, "blog/post_detail.html", {"slug": slug})