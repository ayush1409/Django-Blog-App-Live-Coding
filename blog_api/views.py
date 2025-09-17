from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .serializers import SignupSerializer, BlogPostSerializer, UserSerializer
from .models import BlogPost

User = get_user_model()

# ---- auth endpoints ----
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    Sign up endpoint:
    POST { username, email, password } -> creates user and returns token
    """
    ser = SignupSerializer(data=request.data)
    if ser.is_valid():
        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        data = {'token': token.key, 'user': UserSerializer(user).data}
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Simple login returning token:
    POST { username, password } -> token
    """
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'detail': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'detail': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user).data})


# ---- blog CRUD ----
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Create a blog post. By default posts are drafts (is_draft True).
    To publish immediately, set is_draft to False in body; server will set published_at.
    """
    ser = BlogPostSerializer(data=request.data, context={'request': request})
    if ser.is_valid():
        post = ser.save()
        return Response(BlogPostSerializer(post).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    """
    List my posts. Optional query param: drafts=true to only fetch drafts.
    """
    qs = BlogPost.objects.filter(author=request.user)
    drafts = request.query_params.get('drafts')
    if drafts and drafts.lower() == 'true':
        qs = qs.filter(is_draft=True)
    else:
        # default: show all (drafts + published) for owner
        qs = qs.order_by('-created_at')
    ser = BlogPostSerializer(qs, many=True)
    return Response(ser.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    """
    Retrieve / update / delete a post (only owner can update/delete).
    """
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'GET':
        # owners can see drafts, others should be blocked if draft
        if post.is_draft and post.author != request.user:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BlogPostSerializer(post).data)

    # below: update or delete requires ownership
    if post.author != request.user:
        return Response({'detail': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        ser = BlogPostSerializer(post, data=request.data, partial=True, context={'request': request})
        if ser.is_valid():
            post = ser.save()
            return Response(BlogPostSerializer(post).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- feed (others posts) ----
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed_view(request):
    """
    Show posts by other users, only published (is_draft=False), sorted by published_at desc.
    Supports pagination via page query param.
    """
    qs = BlogPost.objects.filter(is_draft=False).exclude(author=request.user).order_by('-published_at', '-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 5  # small page size for demo; change as needed
    page = paginator.paginate_queryset(qs, request)
    ser = BlogPostSerializer(page, many=True)
    return paginator.get_paginated_response(ser.data)


# ---- timeline (all published posts, including own) with pagination ----
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def timeline_view(request):
    """
    Timeline shows ALL published posts (including yours), sorted by published_at desc.
    Supports pagination.
    """
    qs = BlogPost.objects.filter(is_draft=False).order_by('-published_at', '-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(qs, request)
    ser = BlogPostSerializer(page, many=True)
    return paginator.get_paginated_response(ser.data)
