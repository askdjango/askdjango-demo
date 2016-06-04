from django.conf.urls import url

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import NaverProvider
from .views import login_by_token

urlpatterns = default_urlpatterns(NaverProvider)

urlpatterns += [
    url(r'^naver/login/token/$', login_by_token, name='naver_login_by_token'),
]

