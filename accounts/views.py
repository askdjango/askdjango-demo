from django.conf import settings
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm


signup = CreateView.as_view(
        form_class=UserCreationForm, template_name='form.html',
        success_url=settings.LOGIN_URL)

