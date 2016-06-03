from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views

urlpatterns = [
    url(r'^login/$', login, name='login', kwargs={'template_name': 'form.html'}),
    url(r'^logout/$', logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
]

