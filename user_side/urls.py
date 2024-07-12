from django.urls import path
from .views import *



urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
]