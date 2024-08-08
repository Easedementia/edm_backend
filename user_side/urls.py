from django.urls import path
from .views import UserSignupView, UserLoginView, VerifyOTP, GoogleAuthLogin, EnquiryView, ListServicesView, DoctorProfileListView, DoctorTimeSlotsView, CreateAppointmentView, StartPayment, HandlePaymentSuccess



urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTP.as_view(), name='otp-verification'),
    path('user-google-auth/', GoogleAuthLogin.as_view(), name='user-google-auth'),
    path('enquiries/', EnquiryView.as_view(), name='enquiries'),
    path('services/', ListServicesView.as_view(), name='services'),
    path('doctors-list/', DoctorProfileListView.as_view(), name='doctors-list'),
    path('doctor-time-slots/<int:doctor_id>/', DoctorTimeSlotsView.as_view(), name='doctor-time-slots'),
    path('create-appointment/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('pay/<int:id>/', StartPayment.as_view(), name="payment"),
    path('payment/success/', HandlePaymentSuccess.as_view(), name="payment_success"),
]