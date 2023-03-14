
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


class Profiles(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('date_joined').reverse()

    def get_permissions(self):
        if str(self.request.method) == "POST":
            return [permissions.AllowAny()]

        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) == "DELETE":
            return [permissions.IsAdminUser()]

        if str(self.request.method) in ("PUT", "PATCH", "OPTIONS"):
            return [custom_permissions.IsOwner()]

    def get_serializer_class(self):
        class serializer_class(serializers.ModelSerializer):

            class Meta:
                model = User
                fields = ("id", "email", "first_name", "last_name", "birthday", "password")

                extra_kwargs = dict()
                extra_kwargs['email'] = {'required': True,
                                         'allow_blank': False,
                                         'validators': [UniqueValidator(queryset=User.objects.all(),
                                                                        message='Email has already exist')]}
                extra_kwargs['first_name'] = {'required': True, 'allow_blank': False}
                extra_kwargs['last_name'] = {'required': True, 'allow_blank': False}
                extra_kwargs['birthday'] = {'required': True}
                extra_kwargs['password'] = {'required': True, 'write_only': True}

            def create(self, validated_data):
                user = tools.create_user(validated_data)
                return user

            def update(self, instance, validated_data):
                instance.first_name = validated_data.get('first_name', instance.first_name)
                instance.last_name = validated_data.get('last_name', instance.last_name)
                instance.birthday = validated_data.get('birthday', instance.birthday)
                if validated_data.get('password'):
                    instance.set_password(validated_data['password'])

                instance.save(update_fields=['first_name', 'last_name', 'birthday', 'password'])
                return instance

        if str(self.request.method) != 'POST':
            serializer_class.Meta.extra_kwargs['email']['required'] = False
            serializer_class.Meta.extra_kwargs['email']['read_only'] = True

        if str(self.request.method) in ("PUT", "PATCH"):
            serializer_class.Meta.extra_kwargs['first_name']['required'] = False
            serializer_class.Meta.extra_kwargs['last_name']['required'] = False
            serializer_class.Meta.extra_kwargs['last_name']['required'] = False
            serializer_class.Meta.extra_kwargs['birthday']['required'] = False
            serializer_class.Meta.extra_kwargs['password']['required'] = False

        return serializer_class


class Comments(viewsets.ModelViewSet):

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        return Comment.objects.filter(user=user).all().order_by('id').reverse()

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) in ("POST", "DELETE", "OPTIONS"):
            return [custom_permissions.IsOwner()]

        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        class serializer_class(serializers.ModelSerializer):

            post = serializers.IntegerField(
                allow_null=False,
                required=True,
                validators=[
                    custom_validators.ExistInValidator(queryset=Comment.objects.all(), message='post {} not exist')
                ]
            )

            class Meta:
                model = Comment
                fields = ('id', 'post', 'comment')

                extra_kwargs = dict()
                extra_kwargs['comment'] = {'required': True, 'allow_blank': False}

            def create(self, validated_data):
                user = get_object_or_404(User, username=self.context.get('request').user)
                post = get_object_or_404(Post, id=validated_data['post'])

                comment = Comment(user=user, post=post, comment=validated_data['comment'])
                comment.save()
                return comment

        return serializer_class


class Likes(viewsets.ModelViewSet):

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

    class serializer_class(serializers.ModelSerializer):

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


class Posts(viewsets.ModelViewSet):

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        return Post.objects.filter(user=user).all().order_by('id').reverse()

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) in ("POST", "DELETE", "OPTIONS"):
            return [custom_permissions.IsOwner()]

        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        class serializer_class(serializers.ModelSerializer):

            image = serializers.ImageField(required=True, allow_null=False)

            if self.request.method == 'POST':
                tags = serializers.CharField(required=False, allow_blank=False, default='')

            class Meta:
                model = Post
                fields = ("id", "image", "tags")
                extra_kwargs = dict()

            def create(self, validated_data):
                user = get_object_or_404(User, username=self.context.get('request').user)
                post = tools.add_new_post(user, **validated_data)
                return post

        return serializer_class


class Subscriptions(viewsets.ModelViewSet):
    paginate_by = 100

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        if str(self.request.method) in ("POST", "DELETE", "OPTIONS"):
            return [custom_permissions.IsOwner()]

        return [permissions.IsAdminUser()]

    class serializer_class(serializers.ModelSerializer):

        to_user = serializers.IntegerField(
            required=True,
            allow_null=False,
            validators=[custom_validators.ExistInValidator(queryset=User.objects.all(),
                                                           message='That user {} doesnt exist')])

        class Meta:
            model = Subscription
            fields = ("to_user",)

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

    def get_permissions(self):
        if str(self.request.method) in ("GET", "HEAD"):
            return [permissions.IsAuthenticated()]

        return [permissions.IsAdminUser()]

    class serializer_class(serializers.ModelSerializer):
        class Meta:
            model = Subscription
            fields = ("from_user",)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['profile'])
        return Subscription.objects.filter(to_user=user).all().order_by('from_user')

    def get_object(self):
        user = get_object_or_404(User, id=int(self.kwargs['profile']))
        from_user = get_object_or_404(User, id=int(self.kwargs['pk']))
        return get_object_or_404(Subscription, from_user=from_user, to_user=user)
