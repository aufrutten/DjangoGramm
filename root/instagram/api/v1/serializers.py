from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404

from instagram.models import User, Comment, Post, Like, Subscription
from . import custom_validators


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ["id", "user", "tags"]
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        user = get_object_or_404(User, username=self.context.get('request').user)
        post = tools.add_new_post(user, **validated_data)
        return post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "comment"]
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        print(validated_data)
        user = get_object_or_404(User, username=self.context.get('request').user)
        post = get_object_or_404(Post, id=self.context.get('request').parser_context.get('kwargs')['post'])
        comment = Comment(user=user, post=post, comment=validated_data['comment'])
        comment.save()
        return comment


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["user"]
        extra_kwargs = {'user': {'read_only': True}}


class ProfileSerializer(serializers.ModelSerializer):

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


class SubscriptionSerializer(serializers.ModelSerializer):

    to_user = serializers.IntegerField(
        required=True,
        allow_null=False,
        validators=[custom_validators.ExistInValidator(queryset=User.objects.all(),
                                                       message='That user {} doesnt exist')])

    class Meta:
        model = Subscription
        fields = ("to_user",)


class SubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("from_user",)
