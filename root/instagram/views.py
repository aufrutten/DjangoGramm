import json

import django.db.models.query
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register
from django.core.handlers.wsgi import WSGIRequest

from .models import Post, User, Like, Comment, Tag, Subscription
from . import tools
from . import forms


@register.filter
def get_range(value):
    if isinstance(value, list):
        return range(len(value))
    return range(value)


@login_required
def post_view(request: WSGIRequest, post: int):
    post = tools.get_post(post)
    return render(request, 'gramm/parts/post.html', context={'post': post})


@login_required
def subscriptions(request: WSGIRequest, profile):
    profile = get_object_or_404(User, id=profile)
    context = {'profile': profile, 'subscriptions': Subscription.objects.filter(from_user=profile).all()}
    return render(request, 'gramm/subscriptions.html', status=200, context=context)


@login_required
def comments(request: WSGIRequest, post):
    post = tools.get_post(post)
    user = get_object_or_404(User, username=request.user)
    form = forms.CommentsForm()

    if request.method == "POST":
        form = forms.CommentsForm(request.POST)
        form.request = request
        if form.is_valid():
            comment = Comment(user=user, post=post, comment=form.cleaned_data.get('comment'))
            comment.save()
            post.comments.appendleft(comment)
    return render(request, 'gramm/comments.html', status=200, context={'post': post, 'form': form})


@login_required
def _profile(request: WSGIRequest, profile):
    profile = get_object_or_404(User, id=profile)
    return render(request, 'gramm/profile.html', status=200, context={'profile': profile})


@login_required
def home(request: WSGIRequest):
    return render(request, 'gramm/home.html', status=200)


@login_required
def add_post(request: WSGIRequest):
    if request.method == "POST":
        form = forms.AddPostForm(request.POST, request.FILES)
        form.request = request
        if form.is_valid():
            form.save()
            return redirect(reverse("profile", args=[request.user.id]))
        return render(request, 'gramm/add_post.html', context={'form': form})
    return render(request, 'gramm/add_post.html', context={'form': forms.AddPostForm()})


@tools.anonymous_required
def login(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SingInForm(request.POST)
        if form.is_valid():

            user = get_object_or_404(User, username=form.cleaned_data.get('email'))
            if not user.is_active:
                return redirect(reverse('confirm_email', args=[user.email]))

            user_auth = authenticate(request, username=user.username, password=form.cleaned_data.get('password'))
            form.add_error('password', "Password isn't correct")

            if user_auth:
                auth_login(request, user_auth)
                return redirect(reverse('profile', args=[request.user.id]))

        return render(request, 'gramm/login.html', status=401, context={'form': form})
    return render(request, 'gramm/login.html', status=401, context={'form': forms.SingInForm()})


@tools.anonymous_required
def email_confirm(request: WSGIRequest, email):
    user = get_object_or_404(User, email=email)

    if user.is_active:
        return redirect(reverse('login'))

    if request.method == "POST":
        form = forms.ConfirmEmailForm(request.POST)
        form.code_compare = user.confirm_code

        if form.is_valid():

            if form.cleaned_data.get('delete_account'):
                user.delete()
                return redirect(reverse('register'))

            user.is_active = True
            user.save()

            return redirect(reverse('login'))
        return render(request, 'gramm/email_confirm.html', context={'email': user.email, 'form': form})
    return render(request, 'gramm/email_confirm.html', context={'email': user.email, 'form': forms.ConfirmEmailForm()})


@tools.anonymous_required
def register(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('confirm_email', args=[form.cleaned_data.get('email')]))
        return render(request, 'gramm/register.html', context={'form': form})
    return render(request, 'gramm/register.html', context={'form': forms.SignUpForm()})
