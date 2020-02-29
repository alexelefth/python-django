from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_user, name='login'),
    path('with_csrf_token', views.with_csrf_token, name='with_csrf_token'),
    path('without_csrf_token', views.without_csrf_token, name='without_csrf_token'),
    path('logout', views.logout_user, name='logout'),
    path('upload_file', views.upload_file, name='upload_file'),
]