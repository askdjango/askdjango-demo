from django.conf import settings

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


AUTH_HOST = 'https://kauth.kakao.com'

API_VERSION = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('kakao',  {}).get('VERSION', 'v1')
API_URL = 'https://kapi.kakao.com/' + API_VERSION


class KakaoAccount(ProviderAccount):
    @property
    def properties(self):
        return self.account.extra_data['properties']

    def get_avatar_url(self):
        return self.properties['profile_image']  # or 'thumbnail_image'

    def to_str(self):
        dflt = super(KakaoAccount, self).to_str()
        return self.properties['nickname'] or dflt


class KakaoProvider(OAuth2Provider):
    id = 'kakao'
    name = 'Kakao'
    package = 'accounts.providers.kakao'
    account_class = KakaoAccount

    def sociallogin_from_response(self, request, response):
        sociallogin = super(KakaoProvider, self).sociallogin_from_response(request, response)
        if not sociallogin.user.username:
            sociallogin.user.username = 'kakao_%s' % sociallogin.account.extra_data['id']
        return sociallogin

    def extract_uid(self, data):
        return data['id']

providers.registry.register(KakaoProvider)

