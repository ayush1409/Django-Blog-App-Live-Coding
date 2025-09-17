from django.db import models
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_draft = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
    def __str__(self):
        return f"{self.title} by {self.author}"
