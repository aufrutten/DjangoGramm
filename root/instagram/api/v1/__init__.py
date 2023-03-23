
from rest_framework import routers

from . import profile
from . import posts

# <-----API-ROUTER-VERSION-1----->
router = routers.DefaultRouter()

# <-----PROFILES----------------->
router.register(r'profiles/(?P<profile>[^/.]+)/likes', profile.Likes, basename='profile_likes')
router.register(r'profiles/(?P<profile>[^/.]+)/subscriptions', profile.Subscriptions, basename='profile_subscriptions')
router.register(r'profiles/(?P<profile>[^/.]+)/subscribers', profile.Subscribers, basename='profile_subscribers')

# <-----POSTS-------------------->
router.register(r'posts/(?P<post>[^/.]+)/likes', posts.Likes, basename='post_likes')
