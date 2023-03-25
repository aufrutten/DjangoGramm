
__all__ = ('Likes',)

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import get_object_or_404

from instagram.models import User, Comment, Post, Like
from instagram import tools
from . import custom_permissions


class LikesSerializer_class(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["user"]
        extra_kwargs = {'user': {'read_only': True}}


class Likes(viewsets.ModelViewSet):
    serializer_class = LikesSerializer_class

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD", "POST"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user)
        post = get_object_or_404(Post, id=kwargs['post'])
        like = tools.do_like(user, post)

        if like:
            return Response({'detail': f'Done! Liked! Post {post.id}'},
                            status=status.HTTP_201_CREATED)
        return Response({'detail': f'Done! Unliked! Post {post.id}'},
                        status=status.HTTP_200_OK)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post'])
        return Like.objects.filter(post=post).all().order_by('user')

