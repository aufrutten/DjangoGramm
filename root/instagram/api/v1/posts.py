
__all__ = ('Profiles', 'Comments', 'Likes')

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import get_object_or_404

from ...models import User, Comment, Post, Like
from ... import tools
from . import custom_permissions


class Posts(viewsets.ModelViewSet):

    queryset = Post.objects.all().order_by('id').reverse()

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD", "POST"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        class serializer_class(serializers.ModelSerializer):

            image = serializers.ImageField(required=True, allow_null=False)

            if self.request.method == 'POST':
                tags = serializers.CharField(required=False, allow_blank=False, default='')

            class Meta:
                model = Post
                fields = ["id", "user", "image", "tags"]
                extra_kwargs = {'user': {'read_only': True}}

            def create(self, validated_data):
                user = get_object_or_404(User, username=self.context.get('request').user)
                post = tools.add_new_post(user, **validated_data)
                return post

        return serializer_class


class Comments(viewsets.ModelViewSet):

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD", "POST"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        class serializer_class(serializers.ModelSerializer):
            class Meta:
                model = Comment
                fields = ["id", "user", "comment"]
                extra_kwargs = {'user': {'read_only': True}}

            def create(self, validated_data):
                user = get_object_or_404(User, username=self.context.get('request').user)
                post = get_object_or_404(Post, id=self.context.get('request').parser_context.get('kwargs')['post'])
                comment = Comment(user=user, post=post, comment=validated_data['comment'])
                comment.save()
                return comment

        return serializer_class

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post'])
        return Comment.objects.filter(post=post).all().order_by('id').reverse()


class Likes(viewsets.ModelViewSet):

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD", "POST"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    class serializer_class(serializers.ModelSerializer):
        class Meta:
            model = Like
            fields = ["user"]
            extra_kwargs = {'user': {'read_only': True}}

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


class Profile(viewsets.ModelViewSet):

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    class serializer_class(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "email", "first_name", "last_name", "birthday"]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post'])
        return User.objects.filter(id=post.user.id).all()
