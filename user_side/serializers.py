from rest_framework import serializers
from .models import *



#UserRegistration Serializer
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'fullname', 'email', 'mobile', 
            'password', 'profile_picture', 'is_blocked', 
            'is_active', 'is_verified'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            fullname=validated_data['fullname'],
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            password=validated_data['password'],
            profile_picture=validated_data.get('profile_picture', None),
            is_blocked=validated_data.get('is_blocked', False),
            is_active=validated_data.get('is_active', True),
            is_verified=validated_data.get('is_verified', False)
        )
        user.is_active = True
        user.save()
        return user
    
    # def create(self, validated_data):
    #     user = CustomUser.objects.create_user(**validated_data)
    #     return user 



class verifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()




class GoogleUserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']

    
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        fullname = validated_data.pop('fullname')
        user = CustomUser.objects.create(email=email, fullname=fullname)
        user.save()
        return user
    


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiries
        fields = '__all__'

    


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile.objects.all(), required=True)
    class Meta:
        model = Appointment
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'




class FirstPersonClientDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstPersonClientDetails
        fields = '__all__'



class SelfAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfAssessment
        fields = ['id', 'fullname', 'email', 'mobile', 'user_id', 'date_taken', 'score']