from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from user_side.serializers import *
from .models import *
from user_side.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404   

# Create your views here.



class AdminLoginView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')

        password = request.data.get('password')
        print('******email******', email)


        user = authenticate(request, email=email, password=password)
        print('***********', user)

        if user is not None and user.is_staff:
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user':{
                    'id': user.id,
                    'email': user.email,
                    'fullname': user.fullname,
                    'mobile': user.mobile,
                }
            }
            return Response(tokens, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        



class UserListView(APIView):
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    


class UserUpdateView(APIView):
    def patch(self, request, email):
        try:
            user = CustomUser.objects.get(email=email)
            user.is_blocked = request.data.get('is_blocked', user.is_blocked)
            user.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    


class AddServiceView(APIView):
    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ServiceList(APIView):
    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceDetail(APIView):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def put(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class DoctorProfileCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class DoctorProfileListView(APIView):
    def get(self, request):
        doctors = DoctorProfile.objects.all()
        serializer = DoctorProfileSerializer(doctors, many=True, context={'request': request})
        return Response(serializer.data)
    


class DoctorProfileDetailView(APIView):
    def get(self, request, id):
        try:
            doctor = DoctorProfile.objects.get(id=id)
        except DoctorProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = DoctorProfileSerializer(doctor, context={'request': request})
        return Response(serializer.data)
    

    def put(self, request, id):
        try:
            doctor = DoctorProfile.objects.get(id=id)
        except DoctorProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DoctorProfileSerializer(doctor, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class TimeSlotCreateView(APIView):
    def get(self, request):
        timeslots = TimeSlot.objects.all()
        serializer = TimeSlotSerializer(timeslots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TimeSlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("SERIALIZER ERRORS:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class TimeSlotListView(APIView):
    def get(self, request, *args, **kwargs):
        time_slots = TimeSlot.objects.all()
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class AppointmentListView(APIView):
    def get(self, request):
        try:
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class UpdateAppointmentStatusView(APIView):
    def put(self, request, id):
        try:
            appointment = Order.objects.get(id=id)
            new_status = request.data.get('status')
            if new_status in dict(Order.STATUS_CHOICES).keys():
                appointment.status = new_status
                appointment.save()
                return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        