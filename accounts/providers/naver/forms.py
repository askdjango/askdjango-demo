from django import forms


class NaverConnectForm(forms.Form):
    access_token = forms.CharField(required=True)

