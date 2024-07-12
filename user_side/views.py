import logging
from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.views import APIView,Response
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.middleware import csrf
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .emails import *

# Create your views here.


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
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
                user = serializer.save()
                print("***USER:***", user)
                print("-----EMAIL----", serializer.data['email'])
                # send_otp_via_email(serializer.data['email'])
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
        data = request.data
        response = Response()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)

        if user and user.is_blocked == True:
            return Response({"Blocked": "This account is blocked!"}, status=status.HTTP_404_NOT_FOUND)

        elif user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response = JsonResponse({
                    "data": data,
                    "user": {
                        "id": user.id,
                        "username": user.email,
                        "name": user.first_name,
                    }
                })
                response.data = {"Success" : "Login successfully","data":data}
                return response
            else:
                return Response({"No active" : "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Invalid" : "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)
