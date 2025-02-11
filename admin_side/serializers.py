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

    def validate_mobile(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        if len(value) != 10:  # Adjust the length check based on your requirements
            raise serializers.ValidationError("Mobile number must be 10 digits.")
        return value
    

    def validate_consulting_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Consulting fee must be a positive number.")
        return value



class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.doctor_name')
    class Meta:
        model = TimeSlot
        fields = ['id', 'day', 'start_time', 'end_time', 'doctor', 'doctor_name', 'is_booked']

    start_time = serializers.TimeField(format='%H:%M:%S')  # Ensure correct time format
    end_time = serializers.TimeField(format='%H:%M:%S')



