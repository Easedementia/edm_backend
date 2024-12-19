import logging
from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer, verifyAccountSerializer, GoogleUserSerializer, EnquirySerializer, AppointmentSerializer, OrderSerializer, FirstPersonClientDetailsSerializer
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
from django.middleware.csrf import get_token
from django.utils.timezone import make_aware

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


# class UserSignupView(APIView):
#     def post(self, request, format=None):
#         data = request.data

#         required_fields = ['fullname', 'email', 'mobile', 'password']
#         missing_fields = [field for field in required_fields if field not in data]

#         if missing_fields:
#             return Response(
#                 {field: f'{field} is required' for field in missing_fields}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         serializer = CustomUserSerializer(data=data)

#         if serializer.is_valid():
#             try:
#                 user = serializer.save()
#                 send_otp_via_email(serializer.data['email'])
#                 return Response(
#                     {
#                         'message': 'User created successfully, Check email.',
#                         'email': user.email,
#                         'data': serializer.data,
#                     },
#                     status=status.HTTP_201_CREATED
#                 )
#             except Exception as e:
#                 return Response(
#                     {'error': 'An error occurred while creating the user'},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


    



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserLoginView(APIView):
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)

        # Attempt to retrieve the user by email directly from CustomUser
        user = get_object_or_404(CustomUser, email=email)

        # Check if the user is inactive
        if not user.is_active:
            return Response({"No active": "This account is not active!!"}, status=status.HTTP_403_FORBIDDEN)

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        # If user is authenticated
        if user is not None:
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
            return JsonResponse(response_data, status=status.HTTP_200_OK)
        else:
            # Authentication failed, incorrect username or password
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
        email = data.get('email', None)
        fullname = data.get('fullname', None)

        print(f"Email: {email}, Fullname: {fullname}")

        try:
            user = CustomUser.objects.get(email=email)

            print(f"User found: {user.fullname}")

            if user.is_active:
                data = get_tokens_for_user(user)
                response = JsonResponse({
                    "Success": "Login successfully",
                    "data": data,
                    "user": {
                        "id": user.id,
                        "username": user.email,
                        "name": user.fullname,
                    }
                })
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["access"],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                get_token(request)
                return response
            else:
                return JsonResponse({"error": "User inactive"}, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            serializer = GoogleUserSerializer(data={
                'email': email,
                'fullname': fullname,
            })
            if serializer.is_valid():
                user = serializer.save()
                data = get_tokens_for_user(user)
                response = JsonResponse({
                    "Success": "User registered and logged in successfully",
                    "data": data,
                    "user": {
                        "id": user.id,
                        "username": user.email,
                        "name": user.fullname,  # Return the fullname
                    }
                })
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["access"],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                get_token(request)
                return response

            return JsonResponse({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)






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
        category = request.query_params.get('category')
        if category:
            doctors = DoctorProfile.objects.filter(category=category)
        else:
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
        selected_date = res.get('selected_date', None)
        print("Selected Date:", selected_date)

        if not appointment_id:
            return Response({'error': 'Appointment ID not provided'}, status=400)
        
        if not selected_date:
            return Response({'error': 'Selected date not provided'}, status=400)
            

        print('Order Payment ID:', ord_id)

        try:
            selected_date = datetime.strptime(selected_date, "%B %d, %Y")
            selected_date = make_aware(selected_date)
            print("UPDATED SELECTED DATE:", selected_date)
        except ValueError:
            return Response({'error': 'Invalid date format. Expected format: November 26, 2024'}, status=400)
        

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

        # meet_link = create_google_meet_space()
        # if meet_link:
        #     order.meet_link = meet_link
        # else:
        #     return Response({'error': 'Failed to create Google Meet Link'}, status=500)
        
        order.save()

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.is_booked = True
            appointment.save()
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=404)
        

        try:
            timeslot = TimeSlot.objects.get(id=slot_id)
            BookedSlot.objects.create(
                timeslot = timeslot,
                date = selected_date,
                is_booked = True
            )
            # timeslot.is_booked = True
            # timeslot.save()
        except TimeSlot.DoesNotExist:
            return Response({'error': 'Timeslot not found'}, status=404)
        

        self.send_order_confirmation_email(order)

        res_data = {
            'message': 'Payment successfully received, appointment is booked, and Google Meet link is generated!',
            # 'meet_link': meet_link
        }

        return Response(res_data)
    


    def send_order_confirmation_email(self, order):
        subject = 'Appointment Confirmation'
        message = (
            f"Dear {order.user_name}, \n\n"
            f"Thank you for making an appointment with Easedementia Technologies!\n"
            f"The appointment details is given below:\n\n"
            f"Doctor: {order.doctor_name}\n"
            f"Date: {order.time_slot_date}\n"
            f"Time: {order.time_slot_start_time}\n\n"
            f"Google Meet Link: {order.meet_link}\n\n"
            f"Best regards, \nEasedementia Technologies"
        )
        recipient_list = [order.user_email]

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            print("Appointment confirmation email send successfully!")
        except Exception as e:
            print(f"An error occured while sending mail: {e}")
    




class CreateMeetView(APIView):
    def get(self, request):
        meet_link = create_google_meet_space()
        if meet_link:
            return JsonResponse({'meet_link': meet_link})
        else:
            return JsonResponse({'error': 'Failed to create Google Meet link'}, status=500)
        


class UserDetailsView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)  
            serializer = CustomUserSerializer(user) 
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserProfilePictureUpload(APIView):
    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, pk=user_id)

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
            user.save()

            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No profile picture provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        



class UserAppointmentsView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointments = Order.objects.filter(user_id=user_id)
            serializer = OrderSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserAssessmentHistoryView(APIView):
    def get(self, request):
        print("***ENTRY***")
        user_id = request.GET.get('user_id')
        print("USER ID:", user_id)

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            print("***Assessment history***")
            assessments = FirstPersonClientDetails.objects.filter(user_id=user_id)
            print("ASSESSMENTS:", assessments)
            serializer = FirstPersonClientDetailsSerializer(assessments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FirstPersonClientDetailsView(APIView):
    def post(self, request):
        name = request.data.get('name', '')
        if name.strip() == '':
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        first_person_client = FirstPersonClientDetails(
            fullname=name,
            assessment_date = datetime.now().date()
            )
        first_person_client.save()
        return Response({
            'message': "Client details saved successfully", 
            'fullname': name,
            'id': first_person_client.id,
            'assessment_date': first_person_client.assessment_date.strftime("%d/%m/%Y")
        }, status=status.HTTP_201_CREATED)
    



# class UpdateUserToModel(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             user_id = request.data.get('user')
#             print("***USER ID***", user_id)
#             if not user_id:
#                 return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
#             try:
#                 user = CustomUser.objects.get(id=user_id)
#                 print("***USER***", user)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
#             data = request.data.copy()
#             print("***DATA***", data)
#             data['user'] = user.id
#             print("data['user']", data['user'])

#             serializer = FirstPersonClientDetailsSerializer(data=data)
#             print("***SERIALIZER***", serializer)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    




class SendAssessmentEmailView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        fullname = request.data.get('fullname')
        score = request.data.get('score')
        interpretation = request.data.get('interpretation')

        if not all([email, fullname, score, interpretation]):
            return JsonResponse({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)


        subject = 'Your Assessment Results'
        message = f'Hello {fullname}, \n\nYour assessment is complete. \n\nScore: {score}\nInterpretation: {interpretation}\n\nThank you for completing assessment!'
        from_email = 'support.easedementia@gmail.com'
        recipient_list = [email]


        try:
            send_mail(subject, message, from_email, recipient_list)
            return JsonResponse({'message': 'Email sent successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        



class UpdateAssessmentScoreAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Existing logic for updating score and interpretation
        try:
            client_id = request.data.get('clientId')
            print("***Client ID***", client_id)
            score = request.data.get('score')
            print("***Score***", score)
            interpretation = request.data.get('interpretation')
            print("***Interpretaion***", interpretation)


            if not client_id or score is None or not interpretation:
                return Response({'error': 'clientId, score, and interpretation are required fields'}, status=status.HTTP_400_BAD_REQUEST)

            client = FirstPersonClientDetails.objects.get(id=client_id)
            client.assessment_score = score
            client.interpretation = interpretation
            client.save()

            return Response({'message': 'Score and interpretation updated successfully'}, status=status.HTTP_200_OK)
        except FirstPersonClientDetails.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        print("***ENTRY***")
        # Logic to update the 'user' field
        try:
            print("***TRY***")
            user_id = request.data.get('user')
            print("USER ID:", user_id)
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser.objects.get(id=user_id)
                print("+++USER+++", user)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            client_id = request.data.get('clientId')  # Assuming clientId is still required to identify the client
            print("+++CLIENT ID+++", client_id)
            client = FirstPersonClientDetails.objects.get(id=client_id)
            print("+++CLIENT+++", client)
            client.user = user
            print("+++CLIENTUSER+++", client.user)
            client.save()

            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        except FirstPersonClientDetails.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        


class UpdateUserDetails(APIView):
    def put(self, request, client_id):
        try:
            client = FirstPersonClientDetails.objects.get(id=client_id)
            print("CLIENT:", client)
        except FirstPersonClientDetails.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FirstPersonClientDetailsSerializer(client, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User details updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class CheckUserEmail(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email is None:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CustomUser.objects.filter(email=email).exists():
            return Response({'exists':True}, status=status.HTTP_200_OK)
        else:
            return Response({'exists':False}, status=status.HTTP_200_OK)
        



class RegisterNewUserView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        try:
            user = CustomUser.objects.create(
                fullname = data.get('fullname'),
                email = data.get('email'),
                mobile = data.get('mobile'),
                password = make_password(data.get('password'))
            )
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class SubscribeNewsLetter(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get('email')

            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            subscription, created = NewsLetterSubscription.objects.get_or_create(email=email)

            if created:
                return Response({'message': 'Successfully subscribed'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Already subscribed'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        