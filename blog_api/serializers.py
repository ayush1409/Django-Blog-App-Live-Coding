from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BlogPost
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'content', 'is_draft', 'published_at', 'created_at', 'updated_at', 'author')
        read_only_fields = ('created_at', 'updated_at', 'author')

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        if validated_data.get('is_draft') is False and not validated_data.get('published_at'):
            validated_data['published_at'] = timezone.now()
        post = BlogPost.objects.create(author=user, **validated_data)
        return post

    def update(self, instance, validated_data):
        was_draft = instance.is_draft
        is_draft_now = validated_data.get('is_draft', instance.is_draft)
        if was_draft and (is_draft_now is False) and not validated_data.get('published_at'):
            validated_data['published_at'] = timezone.now()
        # apply changes
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
