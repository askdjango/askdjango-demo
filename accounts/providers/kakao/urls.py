from django.conf.urls import url

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import KakaoProvider
from .views import login_by_token

urlpatterns = default_urlpatterns(KakaoProvider)

urlpatterns += [
    url(r'^kakao/login/token/$', login_by_token, name='kakao_login_by_token'),
]

