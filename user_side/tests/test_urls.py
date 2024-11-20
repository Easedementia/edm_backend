from django.test import SimpleTestCase
from django.urls import reverse, resolve
from user_side.views import *



class UserSideURLTests(SimpleTestCase):
    def test_signup_url_resolves(self):
        url = reverse('signup')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserSignupView)

    
    def test_login_url_resolves(self):
        url = reverse('login')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserLoginView)


    def test_verify_otp_url_resolves(self):
        url = reverse('otp-verification')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, VerifyOTP)


    def test_user_google_auth_url_resolves(self):
        url = reverse('user-google-auth')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, GoogleAuthLogin)


    def test_enquiries_url_resolves(self):
        url = reverse('enquiries')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, EnquiryView)


    def test_services_url_resolves(self):
        url = reverse('services')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, ListServicesView)


    def test_doctors_list_url_resolves(self):
        url = reverse('doctors-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DoctorProfileListView)


    def test_doctor_time_slots_url_resolves(self):
        # Test for the doctor-time-slots URL with a doctor_id parameter
        url = reverse('doctor-time-slots', args=[1])  # Example doctor_id = 1
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DoctorTimeSlotsView)


    def test_create_appointment_url_resolves(self):
        url = reverse('create-appointment')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, CreateAppointmentView)


    def test_payment_url_resolves(self):
        url = reverse('payment', args=[1])
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, StartPayment)


    def test_payment_success_url_resolves(self):
        url = reverse('payment_success')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, HandlePaymentSuccess)


    def test_create_meet_url_resolves(self):
        url = reverse('create-meet')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, CreateMeetView)


    def test_user_appointments_url_resolves(self):
        url = reverse('user-appointments')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserAppointmentsView)


    def test_assessments_url_resolves(self):
        url = reverse('assessments')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserAssessmentHistoryView)


    def test_user_details_url_resolves(self):
        url = reverse('user-details')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserDetailsView)


    def test_upload_profile_picture_url_resolves(self):
        url = reverse('upload-profile-picture', args=[1])
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserProfilePictureUpload)


    def test_first_person_client_details_url_resolves(self):
        url = reverse('first-person-client-details')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, FirstPersonClientDetailsView)


    def test_send_first_person_assessment_email_url_resolves(self):
        url = reverse('send-first-person-assessment-email')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, SendAssessmentEmailView)


    def test_update_assessment_score_url_resolves(self):
        url = reverse('update-assessment-score')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UpdateAssessmentScoreAPIView)


    def test_update_first_person_user_details_url_resolves(self):
        url = reverse('update-first-person-user-details', args=[1])
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UpdateUserDetails)


    def test_check_user_email_url_resolves(self):
        url = reverse('check-user-email')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, CheckUserEmail)


    def test_register_new_user_url_resolves(self):
        url = reverse('register-new-user')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, RegisterNewUserView)


    def test_subscribe_newsletter_url_resolves(self):
        url = reverse('subscribe-newsletter')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, SubscribeNewsLetter)


    
