from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),

    # posts
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/mine/', views.my_posts, name='my_posts'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    # feeds / timelines
    path('feed/', views.feed_view, name='feed'),
    path('timeline/', views.timeline_view, name='timeline'),
]