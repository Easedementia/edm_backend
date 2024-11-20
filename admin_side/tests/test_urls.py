from django.test import SimpleTestCase
from django.urls import reverse, resolve
from user_side.models import *
from admin_side.models import *
from admin_side.views import *





class AdminSideURLTests(SimpleTestCase):

    def test_admin_login_url_resolves(self):
        url = reverse('admin-login')  # Reversing the URL name
        resolved_view = resolve(url).func.view_class  # Resolving the URL to the view class
        self.assertEqual(resolved_view, AdminLoginView)  # Verifying the view class

    def test_user_list_url_resolves(self):
        url = reverse('user-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UserListView)


    def test_user_update_url_resolves(self):
        email = 'test@example.com'  # Example email for testing
        url = reverse('user-update', kwargs={'email': email})  # Passing the email as a keyword argument
        resolved_view = resolve(url).func.view_class  # Resolving the URL to the view class
        self.assertEqual(resolved_view, UserUpdateView)


    def test_add_service_url_resolves(self):
        url = reverse('add-service')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, AddServiceView)


    def test_service_list_url_resolves(self):
        url = reverse('service-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, ServiceList)


    def test_service_detail_url_resolves(self):
        url = reverse('service-detail', kwargs={'pk': 1})
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, ServiceDetail)


    def test_doctor_creation_url_resolves(self):
        url = reverse('doctor-creation')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DoctorProfileCreateView)


    def test_doctors_list_url_resolves(self):
        url = reverse('admin-doctors-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DoctorProfileListView)


    def test_doctors_details_url_resolves(self):
        url = reverse('doctors-details', args=[1])
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DoctorProfileDetailView)


    def test_add_timeslots_url_resolves(self):
        url = reverse('add-timeslots')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, TimeSlotCreateView)


    def test_timeslots_list_url_resolves(self):
        url = reverse('timeslots-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, TimeSlotListView)


    def test_appointments_list_url_resolves(self):
        url = reverse('appointments-list')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, AppointmentListView)


    def test_update_appointment_status_url_resolves(self):
        url = reverse('update-appointment-status', args=[1])
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, UpdateAppointmentStatusView)