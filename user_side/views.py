import logging
from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer, verifyAccountSerializer, GoogleUserSerializer
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

load_dotenv()

# Create your views here.
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
print('EMAIL_HOST_USER:',EMAIL_HOST_USER)
print('EMAIL_HOST_PASSWORD:',EMAIL_HOST_PASSWORD)



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