from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)