from django.urls import path
from .views import UserSignupView, UserLoginView, VerifyOTP, GoogleAuthLogin



urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTP.as_view(), name='otp-verification'),
    path('user-google-auth/', GoogleAuthLogin.as_view(), name='user-google-auth'),
]