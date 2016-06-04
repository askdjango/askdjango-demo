import logging
import requests

from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView, OAuth2Error

from .forms import KakaoConnectForm
from .provider import KakaoProvider, AUTH_HOST, API_URL


logger = logging.getLogger(__name__)


def kakao_complete_login(request, app, token):
    provider = providers.registry.by_id(KakaoProvider.id)
    headers = {'authorization': 'Bearer {}'.format(token.token)}
    resp = requests.get(API_URL + '/user/me', headers=headers)
    resp.raise_for_status()
    extra_data = resp.json()
    extra_data['name'] = extra_data['properties']['nickname']
    login = provider.sociallogin_from_response(request, extra_data)
    return login


class KakaoOAuth2Adapter(OAuth2Adapter):
    provider_id = KakaoProvider.id
    authorize_url = AUTH_HOST + '/oauth/authorize'
    access_token_url = AUTH_HOST + '/oauth/token'

    def complete_login(self, request, app, access_token, **kwargs):
        return kakao_complete_login(request, app, access_token)


def get_access_token(self, code):
    data = {
        'client_id': self.consumer_key,
        'redirect_uri': self.callback_url,
        'grant_type': 'authorization_code',
        'code': code,
    }
    params = None
    self._strip_empty_keys(data)
    url = self.access_token_url
    if self.access_token_method == 'GET':
        params = data
        data = None
    # TODO: Proper exception handling
    resp = requests.request(self.access_token_method,
                            url,
                            params=params,
                            data=data)

    # print('---- resp.text for kakao ----')
    # print(resp.text)

    access_token = None
    if resp.status_code == 200:
        # Weibo sends json via 'text/plain;charset=UTF-8'
        if (resp.headers['content-type'].split(';')[0] == 'application/json'
            or resp.text[:2] == '{"'):
            access_token = resp.json()
        else:
            access_token = dict(parse_qsl(resp.text))
    if not access_token or 'access_token' not in access_token:
        raise OAuth2Error('Error retrieving access token: %s'
                          % resp.content)
    return access_token


class KakaoOAuth2CallbackView(OAuth2CallbackView):
    def get_client(self, request, app):
        client = super(KakaoOAuth2CallbackView, self).get_client(request, app)
        setattr(client, 'get_access_token', lambda code: get_access_token(client, code))
        return client


oauth2_login = OAuth2LoginView.adapter_view(KakaoOAuth2Adapter)
oauth2_callback = KakaoOAuth2CallbackView.adapter_view(KakaoOAuth2Adapter)


def login_by_token(request):
    ret = None
    auth_exception = None

    if request.method == 'POST':
        form = KakaoConnectForm(request.POST)
        if form.is_valid():
            try:
                provider = providers.registry.by_id(KakaoProvider.id)
                app = providers.registry.by_id(KakaoProvider.id).get_app(request)
                access_token = form.cleaned_data['access_token']

                token = SocialToken(app=app, token=access_token)
                login = kakao_complete_login(request, app, token)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except requests.RequestException as e:
                logger.exception('Error accessing KAKAO user profile')
                auth_exception = e

    if not ret:
        ret = render_authentication_error(request, KakaoProvider.id, exception+auth_exception)

    return ret 

