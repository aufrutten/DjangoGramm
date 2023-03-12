

from rest_framework import views, generics, serializers, status
from rest_framework.response import Response
from rest_framework import routers
from django.urls import path, include

from . import v1

versions = [
    path('v1/', include(v1.router.urls))
]


class APIRootView(views.APIView):
    """
    This is the root of the API.
    """
    def get(self, request):
        versions_list = []
        protocol = request.scheme
        domain = request.get_host()

        for version in versions:
            try:
                api_version = str(version.__dict__.get('pattern'))[:-1]
                url = f"{protocol}://{domain}/api/{api_version}"
                versions_list.append({f'{api_version}': url})
            except:
                pass
        return Response(versions_list, status=status.HTTP_200_OK)


urlpatterns = [path('', APIRootView.as_view(), name='api_rootAPI')]
urlpatterns += versions
