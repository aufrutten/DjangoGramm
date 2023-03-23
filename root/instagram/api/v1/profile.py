
__all__ = ('Profiles', 'Comments', 'Likes', "Posts", 'Subscribers', 'Subscriptions')

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404

from instagram.models import User, Comment, Post, Like, Subscription
from instagram import tools
from . import custom_permissions
from . import custom_validators


class LikesSerializer_class(serializers.ModelSerializer):
    post = serializers.IntegerField(
        allow_null=False,
        required=True,
        validators=[
            custom_validators.ExistInValidator(queryset=Comment.objects.all(), message='post {} not exist')
        ]
    )

    class Meta:
        model = Like
        fields = ("post",)


class SubscriptionsSerializer_class(serializers.ModelSerializer):

    to_user = serializers.IntegerField(
        required=True,
        allow_null=False,
        validators=[custom_validators.ExistInValidator(queryset=User.objects.all(),
                                                       message='That user {} doesnt exist')])

    class Meta:
        model = Subscription
        fields = ("to_user",)


class SubscribersSerializer_class(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("from_user",)


class Likes(viewsets.ModelViewSet):

    serializer_class = LikesSerializer_class

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        return Like.objects.filter(user=user).all().order_by('post').reverse()

    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        return get_object_or_404(Like, user=user, post=post)

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) in ("POST", "OPTIONS"):
            return [custom_permissions.IsOwner()]

        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        validated_data = self.serializer_class(data={'post': request.data.get('post')})
        if not validated_data.is_valid():
            return Response(validated_data.errors)

        user = get_object_or_404(User, username=request.user)
        post = get_object_or_404(Post, id=validated_data.data['post'])
        like = tools.do_like(user, post)

        if like:
            return Response({'detail': f'Done! Liked! Post {post.id}', 'result': [validated_data.data]},
                            status=status.HTTP_201_CREATED)
        return Response({'detail': f'Done! Unliked! Post {post.id}', 'result': [validated_data.data]},
                        status=status.HTTP_200_OK)


class Subscriptions(viewsets.ModelViewSet):
    paginate_by = 100
    serializer_class = SubscriptionsSerializer_class

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) in ("POST", "DELETE", "OPTIONS"):
            return [custom_permissions.IsOwner()]

        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = get_object_or_404(User, id=int(self.kwargs['profile']))
        return Subscription.objects.filter(from_user=user).all().order_by('to_user')

    def get_object(self):
        user = get_object_or_404(User, id=int(self.kwargs['profile']))
        to_user = get_object_or_404(User, id=int(self.kwargs['pk']))
        return get_object_or_404(Subscription, from_user=user, to_user=to_user)

    def create(self, request, *args, **kwargs):
        validated_data = self.serializer_class(data={'to_user': request.data.get('to_user')})
        if not validated_data.is_valid():
            return Response(validated_data.errors)

        user = get_object_or_404(User, username=request.user)
        to_user = get_object_or_404(User, id=int(validated_data.data['to_user']))
        subscription = tools.do_subscription(user, to_user)

        if subscription:
            return Response({'detail': f'Done! Subscribed! User {to_user.id}', 'result': [validated_data.data]},
                            status=status.HTTP_201_CREATED)
        return Response({'detail': f'Done! Unsubscribed! User {to_user.id}', 'result': [validated_data.data]},
                        status=status.HTTP_200_OK)


class Subscribers(viewsets.ModelViewSet):
    paginate_by = 100
    serializer_class = SubscribersSerializer_class

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        return Subscription.objects.filter(to_user=user).all().order_by('from_user')

    def get_object(self):
        user = get_object_or_404(User, id=int(self.kwargs['profile']))
        from_user = get_object_or_404(User, id=int(self.kwargs['pk']))
        return get_object_or_404(Subscription, from_user=from_user, to_user=user)
