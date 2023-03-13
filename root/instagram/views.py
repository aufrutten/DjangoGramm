import json

import django.db.models.query
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from .models import Post, User, Like, Comment, Tag, Subscription
from . import tools


@login_required
def subscriptions(request, profile):
    profile = get_object_or_404(User, id=profile)
    context = {'profile': profile, 'subscriptions': Subscription.objects.filter(from_user=profile).all()}
    return render(request, 'gramm/subscriptions.html', status=200, context=context)


@login_required
def comments(request, post):
    post = get_object_or_404(Post, id=post)
    if request.method == "POST":
        user = User.objects.get(email=request.user.email)
        comment = request.POST.get('comment')

        comment_obj = Comment(user=user, post=post, comment=comment)
        comment_obj.save()

    comments_list = [{'id': comm_obj.id,
                      'user': comm_obj.user,
                      'comment': comm_obj.comment} for comm_obj in Comment.objects.filter(post=post).all()]

    return render(request, 'gramm/comments.html', status=200, context={'post': post, 'comments': comments_list[::-1]})


@login_required
def _profile(request, profile):
    profile = get_object_or_404(User, id=profile)
    return render(request, 'gramm/profile.html', status=200, context={'profile': profile})


@login_required
def home(request):
    return render(request, 'gramm/home.html', status=200)


@login_required
def add_post(request):

    if request.method == "GET":
        return render(request, 'gramm/add_post.html')

    if request.method == "POST":
        user = get_object_or_404(User, username=request.user)
        image = request.FILES.get('photo')
        tags = request.POST.get('tags')
        tools.add_new_post(user=user, image=image, tags=tags)
        return redirect(reverse("profile", args=[user.id]))


@tools.anonymous_required
def login(request):
    if request.method == "GET":
        return render(request, 'gramm/login.html', status=401)

    if request.method == "POST":
        user = User.objects.filter(email=request.POST.get('email')).first()
        password = request.POST.get('password')

        if user:
            if user.is_active is False:
                return redirect(reverse('confirm_email', args=[user.email]))

            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth:
                auth_login(request, user_auth)
                return redirect(reverse('profile', args=[request.user.id]))

    return render(request, 'gramm/login.html', context={'error': "values isn't correct"}, status=401)


@tools.anonymous_required
def email_confirm(request, email):
    user = get_object_or_404(User, email=email)

    if user.is_active:
        return redirect(reverse('login'))

    if request.method == "GET":
        return render(request, 'gramm/email_confirm.html', context={'email': user.email})

    if request.method == "POST":
        cancel = request.POST.get('cancel')

        if cancel:
            user.delete()
            return redirect(reverse('register'))

        code_inserted = request.POST.get('code')
        code_confirm = user.confirm_code

        if code_confirm == code_inserted:
            user.is_active = True
            user.save()
            return redirect(reverse('login'))
        return render(request, 'base/404.html', status=404)


@tools.anonymous_required
def register(request):
    return render(request, 'gramm/register.html')

