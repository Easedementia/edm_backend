from django.urls import path
from .views import AdminLoginView, UserListView, UserUpdateView, AddServiceView, ServiceList, ServiceDetail, DoctorProfileCreateView, DoctorProfileListView, DoctorProfileDetailView, TimeSlotCreateView, AppointmentListView, UpdateAppointmentStatusView, TimeSlotListView, SelfAssessmentListView, FirstPersonAssessmentListView


urlpatterns = [
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('user-list/', UserListView.as_view(), name='user-list'),
    path('user-update/<str:email>/', UserUpdateView.as_view(), name='user-update'),
    path('add-service/', AddServiceView.as_view(), name='add-service'),
    path('services/', ServiceList.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('add-doctor/', DoctorProfileCreateView.as_view(), name='doctor-creation'),
    path('doctors-list/', DoctorProfileListView.as_view(), name='admin-doctors-list'),
    path('doctors-details/<int:id>/', DoctorProfileDetailView.as_view(), name='doctors-details'),
    path('add-timeslots/', TimeSlotCreateView.as_view(), name='add-timeslots'),
    path('timeslots-list/', TimeSlotListView.as_view(), name='timeslots-list'),
    path('appointments-list/', AppointmentListView.as_view(), name='appointments-list'),
    path('update-appointment-status/<int:id>', UpdateAppointmentStatusView.as_view(), name='update-appointment-status'),
    path('self-assessment-list/', SelfAssessmentListView.as_view(), name="self-assessment-list"),
    path('first-person-assessment-list/', FirstPersonAssessmentListView.as_view(), name='first-person-assessment-list'),
]