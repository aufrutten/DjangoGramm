__all__ = ('anonymous_required',
           'generate_code',
           'get_posts',
           'add_new_post',
           'do_like',
           'do_subscription',
           'create_user')

import json
from random import choice
import string
from multiprocessing import Process

import django.db.models.query
from django.shortcuts import redirect, reverse

from ..models import User, Like, Post, Tag, Subscription


def anonymous_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return func(request, *args, **kwargs)
        return redirect(reverse('home'))

    return wrapper


def generate_code():
    """generation code"""
    characters = string.ascii_letters + string.digits
    return ''.join([choice(characters) for _ in range(6)])


def get_posts(posts_list: django.db.models.query.QuerySet):
    posts = []
    for post_obj in posts_list:
        post = dict()

        post['id'] = post_obj.id
        post['user'] = post_obj.user
        post['image'] = post_obj.image.url
        post['tags'] = ['#' + tag.tag for tag in post_obj.tags.all()]
        post['likes'] = len([like_count for like_count in Like.objects.filter(post=post_obj.id).all()])

        posts.append(post)
    return posts[::-1]


def add_new_post(user, image, tags):
    post = Post(user=user, image=image)
    post.save()

    tags_list = tags.split('#')[1:]
    for tag in tags_list:
        tag = Tag.objects.get_or_create(tag=tag)
        post.tags.add(tag[0])
    return post


def do_like(user, post):
    like = Like.objects.filter(user=user, post=post)
    if like.exists():
        like.delete()
    else:
        return Like.objects.create(user=user, post=post)


def do_subscription(user, to_user):
    subscription = Subscription.objects.filter(from_user=user, to_user=to_user)
    if subscription.exists():
        subscription.delete()
    else:
        return Subscription.objects.create(from_user=user, to_user=to_user)


def create_user(data):
    """data is: request.POST or request.data"""

    if User.objects.filter(email=data.get('email')).exists():
        return None

    user_data = dict()
    user_data['username'] = data.get('email')
    user_data['email'] = data.get('email')
    user_data['first_name'] = data.get('first_name')
    user_data['last_name'] = data.get('last_name')
    user_data['birthday'] = data.get('birthday')
    user_data['password'] = data.get('password')
    user_data['is_active'] = False
    user_data['confirm_code'] = generate_code()

    user = User.objects.create_user(**user_data)

    mail_message = f"Good day! Mr/Miss {user.last_name}\n" \
                   f"Your email: {user.email} has indicated in registration profile\n" \
                   f"If it wasn't you don't do nothing\n" \
                   f"\n" \
                   f"Confirm Code: {user.confirm_code}\n" \
                   f"\n" \
                   f"Have a nice day! aufrutten.com"

    Process(target=user.email_user, args=('Confirm Email', mail_message)).run()

    return user
