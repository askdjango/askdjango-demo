from django.conf import settings

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


AUTH_HOST = 'https://nid.naver.com'

API_VERSION = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('naver',  {}).get('VERSION', 'v1')
API_URL = 'https://openapi.naver.com/' + API_VERSION


class NaverAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data['profile_image']

    def to_str(self):
        dflt = super(NaverAccount, self).to_str()
        return self.account.extra_data.get('email', dflt)


class NaverProvider(OAuth2Provider):
    id = 'naver'
    name = 'Naver'
    package = 'accounts.providers.naver'
    account_class = NaverAccount

    def sociallogin_from_response(self, request, response):
        sociallogin = super(NaverProvider, self).sociallogin_from_response(request, response)
        if not sociallogin.user.username:
            sociallogin.user.username = 'naver_%s' % sociallogin.account.extra_data['id']
        return sociallogin

    def extract_uid(self, data):
        return data['id']


providers.registry.register(NaverProvider)

