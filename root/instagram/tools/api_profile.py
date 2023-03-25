
__all__ = ('anonymous_required',
           'generate_code',
           'get_post',
           'add_new_post',
           'do_like',
           'do_subscription',
           'create_user')

import json
from random import choice
import string
import collections
from multiprocessing import Process

import django.db.models.query
from django.conf import settings
from django.shortcuts import redirect, reverse, get_object_or_404, get_list_or_404
from django.core.mail import send_mail

from ..models import User, Like, Post, Tag, Subscription, Image, Comment


def anonymous_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return func(request, *args, **kwargs)
        return redirect(reverse('home'))
    return wrapper


def generate_code():
    """generation code"""
    characters = string.ascii_letters + string.digits
    return ''.join([choice(characters) for _ in range(settings.LENGTH_OF_CODE_CONFIRM)])


def get_post(post_id):
    post = get_object_or_404(Post, id=post_id)
    post.images = get_list_or_404(Image, post=post_id)
    post.comments = collections.deque(Comment.objects.filter(post=post_id).all()[::-1])
    return post


def add_new_post(user, images, tags):
    # Creation post
    post = Post(user=user)
    post.save()

    # Appending photos to post
    for image in images:
        img = Image(post=post, image=image)
        img.save()

    # Appending tags to post
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


def create_user(form):
    if str(type(form)) != "<class 'instagram.forms.SignUpForm'>":
        raise TypeError('you must use instagram.forms.SingUpForm')

    user_data = dict()
    user_data['username'] = form.cleaned_data['email'].lower()
    user_data['email'] = form.cleaned_data['email'].lower()
    user_data['first_name'] = form.cleaned_data['first_name'].title()
    user_data['last_name'] = form.cleaned_data['last_name'].title()
    user_data['birthday'] = form.cleaned_data['birthday']
    user_data['password'] = form.cleaned_data['password']
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
