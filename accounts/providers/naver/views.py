import logging
import requests

from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView, OAuth2Error

from bs4 import BeautifulSoup, Tag

from .forms import NaverConnectForm
from .provider import NaverProvider, AUTH_HOST, API_URL


logger = logging.getLogger(__name__)


def naver_complete_login(request, app, token):
    provider = providers.registry.by_id(NaverProvider.id)
    headers = {'authorization': 'Bearer {}'.format(token.token)}
    resp = requests.get(API_URL + '/nid/getUserProfile.xml', headers=headers)
    resp.raise_for_status()

    # print('---- resp.text ----')
    # print(repr(resp.text))

    soup = BeautifulSoup(resp.text, 'html.parser')
    parsed = {}
    for sub in ('result', 'response'):
        props = {}
        for tag in soup.find(sub):
            if isinstance(tag, Tag):
                props[tag.name] = tag.text
        parsed[sub] = props

    extra_data = parsed['response']
    login = provider.sociallogin_from_response(request, extra_data)
    return login


class NaverOAuth2Adapter(OAuth2Adapter):
    provider_id = NaverProvider.id
    authorize_url = AUTH_HOST + '/oauth2.0/authorize'
    access_token_url = AUTH_HOST + '/oauth2.0/token'

    def complete_login(self, request, app, access_token, **kwargs):
        return naver_complete_login(request, app, access_token)


oauth2_login = OAuth2LoginView.adapter_view(NaverOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NaverOAuth2Adapter)


def login_by_token(request):
    ret = None
    auth_exception = None

    if request.method == 'POST':
        form = NaverConnectForm(request.POST)
        if form.is_valid():
            try:
                provider = providers.registry.by_id(NaverProvider.id)
                app = providers.registry.by_id(NaverProvider.id).get_app(request)
                access_token = form.cleaned_data['access_token']

                token = SocialToken(app=app, token=access_token)
                login = naver_complete_login(request, app, token)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except requests.RequestException as e:
                logger.exception('Error accessing NAVER user profile')
                auth_exception = e

    if not ret:
        ret = render_authentication_error(request, NaverProvider.id, exception+auth_exception)

    return ret 

