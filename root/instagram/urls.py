from django.urls import path
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout as auth_logout
from . import views


def root(request):
    return redirect(reverse('home'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('login'))


def handler404(request, exception):
    return render(request, 'base/404.html', status=404)


urlpatterns = [
    path('', root, name='root'),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', logout, name='logout'),
    path('confirm_email/<str:email>', views.email_confirm, name='confirm_email'),

    path('home/', views.home, name='home'),
    path('profiles/<int:profile>', views._profile, name='profile'),
    path('profiles/<int:profile>/subscriptions', views.subscriptions, name='subscriptions'),

    path('posts/', views.add_post, name='add_post'),
    path('posts/<int:post>', views.post_view, name='post'),
    path('posts/<int:post>/comments', views.comments, name='comments'),
]
