from django.core.management.base import BaseCommand
from blog.models import Post
from faker import Faker
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Generate fake blog posts'
    
    def handle(self,*args,**kwargs):
        fake = Faker()
        for _ in range(10):
            title = fake.sentence(nb_words=6)
            content = fake.paragraph(nb_sentences=5)
            slug = slugify(title)[:90] + str(random.randint(1000, 2000))
            
            Post.objects.create(title=title, content=content, slug=slug)
        
        self.stdout.write(self.style.SUCCESS('✅ 10 fake posts created!'))