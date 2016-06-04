from django import forms


class KakaoConnectForm(forms.Form):
    access_token = forms.CharField(required=True)

