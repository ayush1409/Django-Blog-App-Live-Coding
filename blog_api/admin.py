from django.contrib import admin
from .models import BlogPost

# Register your models here.

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_draft', 'published_at', 'created_at')
    list_filter = ('is_draft', 'author')
    search_fields = ('title', 'content')

