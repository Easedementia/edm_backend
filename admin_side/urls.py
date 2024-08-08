from django.urls import path
from .views import AdminLoginView, UserListView, AddServiceView, ServiceList, ServiceDetail, DoctorProfileCreateView, DoctorProfileListView, DoctorProfileDetailView, TimeSlotCreateView


urlpatterns = [
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('user-list/', UserListView.as_view(), name='user-list'),
    path('add-service/', AddServiceView.as_view(), name='add-service'),
    path('services/', ServiceList.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('add-doctor/', DoctorProfileCreateView.as_view(), name='doctor-creation'),
    path('doctors-list/', DoctorProfileListView.as_view(), name='doctors-list'),
    path('doctors-details/<int:id>/', DoctorProfileDetailView.as_view(), name='doctors-details'),
    path('add-timeslots/', TimeSlotCreateView.as_view(), name='add-timeslots'),
]