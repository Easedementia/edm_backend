from rest_framework import serializers
from .models import *
from user_side.models import *


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'mobile', 'is_active']



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = '__all__'



class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.doctor_name')
    class Meta:
        model = TimeSlot
        fields = ['id', 'day', 'start_time', 'end_time', 'doctor', 'doctor_name', 'is_booked']