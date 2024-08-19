import logging
from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer, verifyAccountSerializer, GoogleUserSerializer, EnquirySerializer, AppointmentSerializer, OrderSerializer
from rest_framework.views import APIView,Response
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.middleware import csrf
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .emails import *
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
import os
from dotenv import load_dotenv
from admin_side.models import *
from admin_side.views import *
from admin_side.serializers import *
from rest_framework.exceptions import NotFound
import razorpay
import json
from .utils import create_google_meet_space

load_dotenv()

# Create your views here.
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
print("EMAIL_HOST_USER:", EMAIL_HOST_USER)
print("EMAIL_HOST_PASSWORD", EMAIL_HOST_PASSWORD)



logger = logging.getLogger(__name__)

class UserSignupView(APIView):
    def post(self, request, format=None):
        print("***entry***")
        data = request.data
        print('***REQUEST DATA***', data)

        required_fields = ['fullname', 'email', 'mobile', 'password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return Response(
                {field: f'{field} is required' for field in missing_fields}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CustomUserSerializer(data=data)
        print('***SERIALIZER***', serializer)

        if serializer.is_valid():
            try:
                print("***SERIALIZER IS VALID***")
                # serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
                user = serializer.save()
                print("***USER:***", user)
                print("-----EMAIL----", serializer.data['email'])
                EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
                EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
                print("EMAIL_HOST_USER:", EMAIL_HOST_USER)
                print("EMAIL_HOST_PASSWORD", EMAIL_HOST_PASSWORD)
                send_otp_via_email(serializer.data['email'])
                print("---OTP---")
                return Response(
                    {
                        'message': 'User created successfully, Check email.',
                        'email': user.email,
                        'data': serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                print("***EXCEPTION OCCURRED***", str(e))
                logger.error("Error creating user: %s", str(e))
                return Response(
                    {'error': 'An error occurred while creating the user'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            print("***SERIALIZER ERRORS***", serializer.errors)
            logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserLoginView(APIView):
    def post(self, request, format=None):
        print("***Entry***")
        data = request.data
        print("DATA:", data)
        email = data.get('email', None)
        print("Email:", email)
        password = data.get('password', None)
        print("Password:", password)
        user_details = CustomUser.objects.filter(email=email, password=password)
        print("User details:", user_details)
        user = authenticate(request, email=email, password=password)
        print("User:", user)

        if user is not None:
            if user.is_active:
                tokens = get_tokens_for_user(user)
                response_data = {
                    "data": tokens,
                    "user": {
                        'id': user.id,
                        'email': user.email,
                        'fullname': user.fullname,
                        'mobile': user.mobile,
                    },
                    "Success": "Login successfully"
                }
                csrf.get_token(request)
                return JsonResponse(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_401_UNAUTHORIZED)
        



class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]



class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = verifyAccountSerializer(data=data)

            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']

                user = CustomUser.objects.filter(email=email)
                if not user.exists():
                    return Response({
                    'status': 400,
                    'message': 'something went wrong',
                    'data': 'invalid email'
                })

                if user[0].otp != otp:
                    return Response({
                    'status': 400,
                    'message': "something went wrong",
                    'data': 'wrong otp',
                })

                user = user.first()
                user.is_verified = True
                user.save()

                return Response({
                    'status': 200,
                    'message': 'account verified',
                    'data': serializer.data,
                })

            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })

        except Exception as e:
            print(e)




class GoogleAuthLogin(APIView):
    def post(self, request):
        data = request.data
        print('*****', data)
        email = data.get('email', None)
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            if user is not None:
                if user.is_active:
                    data = get_tokens_for_user(user)
                    response = JsonResponse({
                        "data": data,
                        "user": {
                            "id": user.id,
                            "username": user.email,
                            "name": user.fullname,
                        }
                    })
                    response.set_cookie(
                        key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                        value = data["access"],
                        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                    )
                    csrf.get_token(request)
                    response.data = {"Success" : "Login successfully","data":data}
                    return response
        else:
            serializer = GoogleUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = CustomUser.objects.get(email=email)
                if user is not None:
                    if user.is_active:
                        data = get_tokens_for_user(user)
                        response = JsonResponse({
                            "data": data,
                            "user": {
                                "id": user.id,
                                "username": user.email,
                                "name": user.fullname,
                            }
                        })
                        response.set_cookie(
                            key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                            value = data["access"],
                            expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                            secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                            httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                            samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                        )
                        csrf.get_token(request)
                        response.data = {"Success" : "Login successfully","data":data}
                        return response
            else:
                return JsonResponse({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse({"error": "User not found or inactive"}, status=status.HTTP_404_NOT_FOUND)
    



class EnquiryView(APIView):
    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class ListServicesView(APIView):
    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)
    



class DoctorProfileListView(APIView):
    def get(self, request):
        doctors = DoctorProfile.objects.all()
        serializer = DoctorProfileSerializer(doctors, many=True)
        return Response(serializer.data)
    


class DoctorTimeSlotsView(APIView):
    def get(self, request, doctor_id):
        timeslots = TimeSlot.objects.filter(doctor_id=doctor_id)
        serializer = TimeSlotSerializer(timeslots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CreateAppointmentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response({'appointment_id': appointment.id, 'details': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class StartPayment(APIView):
    def post(self, request, id):
        print("*****************************")
        print("REQUEST DATA:", request.data)
        print("*****************************")
        user_id = request.data['user_id']
        user_name = request.data['user_name']
        user_email = request.data['user_email']
        user_mobile = request.data['user_mobile']
        doctor_id = request.data['doctor_id']
        doctor_name = request.data['doctor_name']
        consulting_fee = request.data['consulting_fee']
        selected_date = request.data['selected_date']
        selected_day = request.data['selected_day']
        selected_start_time = request.data['selected_start_time']
        selected_end_time = request.data['selected_end_time']

        try:
            print("***USER DETAILS***")
            user = CustomUser.objects.get(id=user_id)
            print("***USER***", user)
        except CustomUser.DoesNotExist:
            raise NotFound("User not found")


        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            print("Doctor:", doctor)
        except DoctorProfile.DoesNotExist:
            raise NotFound('Doctor not found')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_PUBLIC_KEY, settings.RAZORPAY_SECRET_KEY))


        amount = int(float(consulting_fee) * 100)  # Convert amount to paise
        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })
        try:
            order = Order.objects.create(
                user = user,
                user_name = user_name,
                user_email = user_email,
                doctor = doctor,
                doctor_name = doctor_name,
                order_amount = consulting_fee,
                order_payment_id = payment['id'],
                time_slot_date = selected_date,
                time_slot_day = selected_day,
                time_slot_start_time = selected_start_time,
                time_slot_end_time = selected_end_time
            )
            
            print("******************")
            print('***order***', order)
            print("******************")

            serializer = OrderSerializer(order)
            print('***serializer data***', serializer.data)

            data = {
                "payment": payment,
                "order": serializer.data
            }
            print('***data***', data)
            
            return Response(data)
        
        except Exception as e:
            # Log the error for debugging
            print(f"Error during payment processing: {str(e)}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
        




class HandlePaymentSuccess(APIView):
    def post(self, request):
        print('*********handle_payment_success************')
        try:
            # Ensure proper parsing of request body
            res = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON'}, status=400)

        print('***res***', res)

        ord_id = res.get('razorpay_order_id', "")
        raz_pay_id = res.get('razorpay_payment_id', "")
        raz_signature = res.get('razorpay_signature', "")
        appointment_id = res.get('appointment_id', None)
        slot_id = res.get('slot_id', None)

        if not appointment_id:
            return Response({'error': 'Appointment ID not provided'}, status=400)

        print('Order Payment ID:', ord_id)

        # Get the order by payment_id
        try:
            order = Order.objects.get(order_payment_id=ord_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        # Verify the payment signature with Razorpay
        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }

        client = razorpay.Client(auth=("rzp_test_ZQL2ChZEK9SL7A", "qiIPMJQP7dND0mDggXkRa3Xr"))

        try:
            client.utility.verify_payment_signature(data)
        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Invalid payment signature'}, status=400)

        # Update the order status to paid
        order.isPaid = True
        order.save()

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.is_booked = True
            appointment.save()
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=404)
        

        try:
            timeslot = TimeSlot.objects.get(id=slot_id)
            timeslot.is_booked = True
            timeslot.save()
        except TimeSlot.DoesNotExist:
            return Response({'error': 'Timeslot not found'}, status=404)

        res_data = {
            'message': 'Payment successfully received and appointment is booked!'
        }

        return Response(res_data)
    




class CreateMeetView(APIView):
    def get(self, request):
        meet_link = create_google_meet_space()
        if meet_link:
            return JsonResponse({'meet_link': meet_link})
        else:
            return JsonResponse({'error': 'Failed to create Google Meet link'}, status=500)