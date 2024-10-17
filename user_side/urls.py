from django.urls import path
from .views import UserSignupView, UserLoginView, VerifyOTP, GoogleAuthLogin, EnquiryView, ListServicesView, DoctorProfileListView, DoctorTimeSlotsView, CreateAppointmentView, StartPayment, HandlePaymentSuccess, CreateMeetView, UserAppointmentsView, UserDetailsView, UserProfilePictureUpload, FirstPersonClientDetailsView, SendAssessmentEmailView, UpdateAssessmentScoreAPIView, UpdateUserDetails, CheckUserEmail, RegisterNewUserView, SubscribeNewsLetter, UserAssessmentHistoryView



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
    path('create-meet/', CreateMeetView.as_view(), name='create-meet'),
    path('appointments/', UserAppointmentsView.as_view(), name='user-appointments'),
    path('assessments/', UserAssessmentHistoryView.as_view(), name='assessments'),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('user-profile/<int:user_id>/update/', UserProfilePictureUpload.as_view(), name='upload-profile-picture'),
    path('first-person-client-details/', FirstPersonClientDetailsView.as_view(), name='first-person-client-details'),
    path('send-first-person-assessment-email/', SendAssessmentEmailView.as_view(), name='send-first-person-assessment-email'),
    path('update-first-person-assessment-score/', UpdateAssessmentScoreAPIView.as_view(), name='update-assessment-score'),
    path('update-first-person-user-details/<int:client_id>/', UpdateUserDetails.as_view(), name='update-first-person-user-details'),
    path('check-user-email/', CheckUserEmail.as_view(), name='check-user-email'),
    path('register-new-user/', RegisterNewUserView.as_view(), name='register-new-user'),
    path('subscribe-newsletter/', SubscribeNewsLetter.as_view(), name='subscribe-newsletter'),
    # path('update-user-to-db/', UpdateUserToModel.as_view(), name='update-user-to-db'),
]