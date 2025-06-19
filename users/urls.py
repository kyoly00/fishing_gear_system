from django.urls import path
from .views import root_redirect, login_view, signup_view

urlpatterns = [
    path('', root_redirect, name='root_redirect'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
]