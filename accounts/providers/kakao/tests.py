import json

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.test.client import RequestFactory

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialccount.models import SocialAccount
from allauth.socialaccount import providers
from allauth.socialaccount.providers import registry
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.utils import get_user_model

from .provider import KakaoProvider


@override_settings(
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    LOGIN_REDIRECT_URL='/accounts/profile/',
    ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE,
    SOCIALACCOUNT_PROVIDERS={
        'kakao': {
            'AUTH_PARAMS': {},
            'VERIFIED_EMAIL': False}})
class KakaoTests(create_oauth2_tests(registry.by_id(KakaoProvider.id))):
    kakao_data = '''
        {
            "access_token": "KdXEHXV9BXjqHVAt5w48KBFVdI2YLsv2QqQdWawQQjEAAAFR59PXDg",
            "token_type": "bearer",
            "refresh_token": "elFzFKsbnzAP9LFzaiE6bv-wPH02BLINaFRVjawQQjEAAAFR59PXDA",
            "expires_in": 21599,
            "scope": "story_publish story_read profile"
        }'''

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.kakao_data
        return MockedResponse(200, data)

    def test_username_conflict(self):
        User = get_user_model()
        User.objects.create(username='ask.django')
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount.objects.get(uid='mocked_uid')  # FIXME: mocked uid
        self.assertEqual(socialaccount.user.username, 'askdjango')   # FIXME: mocked username

    def test_username_based_on_provider(self):
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount

