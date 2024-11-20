from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_side.models import CustomUser
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from user_side.views import get_tokens_for_user
from django.test import TestCase
from user_side.models import *
from admin_side.models import *
from user_side.serializers import *
from datetime import date, time
from unittest.mock import patch
from django.core import mail
import json
from django.utils import timezone
from rest_framework.test import APIClient
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile



class UserSignupViewTests(APITestCase):
    
    def setUp(self):
        # You can set up any test data here if needed
        pass
    
    def test_user_signup_success(self):
        url = reverse('signup')  # Assuming 'signup' is the name of the URL for UserSignupView
        data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'mobile': '1234567890',
            'password': 'password123'
        }

        # Mock the send_otp_via_email function to avoid sending real emails
        with patch('user_side.views.send_otp_via_email') as mock_send_otp:
            response = self.client.post(url, data, format='json')
            
            # Ensure the response status is 201 CREATED
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Check the response content
            self.assertEqual(response.data['message'], 'User created successfully, Check email.')
            self.assertEqual(response.data['email'], 'johndoe@example.com')
            
            # Verify that the mock OTP function was called once
            mock_send_otp.assert_called_once_with('johndoe@example.com')

    def test_user_signup_missing_fields(self):
        url = reverse('signup')
        data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            # 'mobile' and 'password' are missing
        }

        response = self.client.post(url, data, format='json')
        
        # Check if the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check that the missing fields are included in the response
        self.assertIn('mobile', response.data)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['mobile'], 'mobile is required')
        self.assertEqual(response.data['password'], 'password is required')

    def test_user_signup_invalid_email(self):
        url = reverse('signup')
        data = {
            'fullname': 'John Doe',
            'email': 'invalid-email',  # Invalid email format
            'mobile': '1234567890',
            'password': 'password123'
        }

        response = self.client.post(url, data, format='json')
        
        # Check if the response status is 400 BAD REQUEST due to invalid email format
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check that the email validation error is present
        self.assertIn('email', response.data)
        
    def test_user_signup_internal_server_error(self):
        url = reverse('signup')
        data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'mobile': '1234567890',
            'password': 'password123'
        }

        # Mock the serializer's save method to raise an exception
        with patch('user_side.views.CustomUserSerializer.save') as mock_save:
            mock_save.side_effect = Exception("Something went wrong")
            response = self.client.post(url, data, format='json')

            # Check if the response status is 500 INTERNAL SERVER ERROR
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'An error occurred while creating the user')




class GetTokensForUserTestCase(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = get_user_model().objects.create_user(
            fullname='John Doe',
            email='johndoe@example.com',
            mobile='1234567890',
            password='password123'
        )

    def test_get_tokens_for_user(self):
        # Call the function to get tokens for the user
        tokens = get_tokens_for_user(self.user)

        # Assert that both the access and refresh tokens are returned
        self.assertIn('refresh', tokens)
        self.assertIn('access', tokens)

        # Assert that the tokens are non-empty strings
        self.assertTrue(isinstance(tokens['refresh'], str))
        self.assertTrue(isinstance(tokens['access'], str))

        # Optionally, check if the refresh token is a valid JWT (simple validation)
        try:
            refresh_token = RefreshToken(tokens['refresh'])
            self.assertTrue(refresh_token)
        except Exception as e:
            self.fail(f"Refresh token is not valid: {e}")
        
        # Check if the access token is a valid JWT (simple validation)
        try:
            access_token = AccessToken(tokens['access'])  # Use AccessToken class for validation
            self.assertTrue(access_token)
        except Exception as e:
            self.fail(f"Access token is not valid: {e}")




class UserLoginViewTestCase(APITestCase):
    def setUp(self):
        # Create a user instance for testing
        self.user = get_user_model().objects.create_user(
            fullname='John Doe',
            email='johndoe@example.com',
            mobile='1234567890',
            password='password123',
        )
        self.url = reverse('login')  # Replace with the actual URL name of your login view


    def test_user_login_successful(self):
        # Test logging in with correct credentials
        data = {
            'email': 'johndoe@example.com',
            'password': 'password123',
        }

        # Send the POST request
        response = self.client.post(self.url, data, format='json')

        # Assert status code 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert response contains token data
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIn('access', response_data['data'])
        self.assertIn('refresh', response_data['data'])

        # Assert user data is returned in the response
        self.assertEqual(response_data['user']['email'], self.user.email)
        self.assertEqual(response_data['user']['fullname'], self.user.fullname)

        # Validate refresh token
        try:
            refresh_token = RefreshToken(response_data['data']['refresh'])
            self.assertTrue(refresh_token)
        except Exception as e:
            self.fail(f"Refresh token validation failed: {e}")

        # Validate access token (use AccessToken instead of RefreshToken)
        try:
            access_token = AccessToken(response_data['data']['access'])
            self.assertTrue(access_token)
        except Exception as e:
            self.fail(f"Access token validation failed: {e}")

        def test_user_login_invalid_credentials(self):
            # Test logging in with invalid credentials
            data = {
                'email': 'johndoe@example.com',
                'password': 'wrongpassword',
            }

            # Send the POST request
            response = self.client.post(self.url, data, format='json')

            # Assert status code 401 (Unauthorized)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Assert response contains the error message
            response_data = response.json()
            self.assertEqual(response_data, {"Invalid": "Invalid username or password!!"})


    def test_user_login_inactive_user(self):
        # Test logging in with a deactivated user
        self.user.is_active = False
        self.user.save()

        data = {
            'email': self.user.email,  # Use the email from the created user
            'password': 'password123',  # Use the password set during user creation
        }

        # Send the POST request
        response = self.client.post(self.url, data, format='json')

        # Assert status code 403 (Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert response contains the error message
        response_data = response.json()
        self.assertEqual(response_data, {"No active": "This account is not active!!"})





class VerifyOTPTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            fullname = 'John Doe',
            email = 'johndoe@example.com',
            mobile = '1234567890',
            otp='123456',
            is_verified = False
        )
        self.url = reverse('otp-verification')
    

    def test_verify_otp_success(self):
        data = {
            'email': 'johndoe@example.com',
            'otp': '123456'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 200)
        self.assertEqual(response.data['message'], 'account verified')

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)


    def test_verify_otp_invalid_email(self):
        data = {
            'email': 'invalid@example.com',
            'otp': '123456'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 400)
        self.assertEqual(response.data['data'], 'invalid email')


    def test_verify_otp_wrong_otp(self):
        data = {
            'email': 'johndoe@example.com',
            'otp': '654321'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 400)
        self.assertEqual(response.data['data'], 'wrong otp')


    def test_verify_otp_invalid_data(self):
        data = {
            'email': 'johndoe@example.com'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 400)
        self.assertIn('otp', response.data['data'])




class GoogleAuthLoginTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('user-google-auth')
        self.existing_user = CustomUser.objects.create_user(
            fullname='Existing User',
            email='existing@example.com',
            mobile='1234567890',
            password='password123',
            is_active=True
        )

    def test_login_existing_user(self):
        data = {
            'email': 'existing@example.com',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIn('refresh', response_data['data'])
        self.assertIn('access', response_data['data'])
        self.assertEqual(response_data['Success'], 'Login successfully')

    def test_register_new_user(self):
        data = {
            'email': 'newuser@example.com',
            'fullname': 'New User',
            'mobile': '9876543210',
            'password': 'newpassword123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIn('user', response_data)
        self.assertEqual(response_data['Success'], 'User registered successfully')

    def test_invalid_data(self):
        data = {
            'email': '',  # Invalid email
            'fullname': '',  # Invalid name
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Invalid data')

    def test_inactive_user(self):
        # Create an inactive user
        inactive_user = CustomUser.objects.create_user(
            fullname='Inactive User',
            email='inactive@example.com',
            mobile='0987654321',
            password='password123',
            is_active=False
        )
        data = {
            'email': 'inactive@example.com',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User inactive')

    def test_user_not_found_creates_user(self):
        # Verify that a new user is registered if the email is not found
        data = {
            'email': 'nonexistent@example.com',
            'fullname': 'Newly Created User',
            'mobile': '1122334455',
            'password': 'safePassword123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIn('user', response_data)
        self.assertEqual(response_data['Success'], 'User registered successfully')





class EnquiryViewTest(APITestCase):
    def setUp(self):
        self.url =  reverse('enquiries')
        self.valid_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'mobile': '1234567890',
            'message': 'This is a test enquiry message.'
        }
        
        self.invalid_data = {
            'fullname': '',
            'email': 'notanemail',
            'mobile': '12345',
            'message': ''
        }


    def test_create_enquiry_with_valid_data(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['fullname'], self.valid_data['fullname'])
        self.assertEqual(response.data['email'], self.valid_data['email'])
        self.assertEqual(response.data['mobile'], self.valid_data['mobile'])
        self.assertEqual(response.data['message'], self.valid_data['message'])
        self.assertEqual(Enquiries.objects.count(), 1)


    def test_create_enquiry_with_invalid_data(self):
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fullname', response.data)
        self.assertIn('email', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(Enquiries.objects.count(), 0)





class ListServicesViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('services')
        # Create some sample service objects
        self.service1 = Service.objects.create(
            title='Service 1',
            description='Description for service 1',
            image='services/service1.svg'
        )
        self.service2 = Service.objects.create(
            title='Service 2',
            description='Description for service 2',
            image='services/service2.svg'
        )

    def test_list_services(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check that the data matches the created services
        self.assertEqual(response.data[0]['title'], self.service1.title)
        self.assertEqual(response.data[0]['description'], self.service1.description)
        self.assertEqual(response.data[1]['title'], self.service2.title)
        self.assertEqual(response.data[1]['description'], self.service2.description)





class DoctorProfileListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('doctors-list')

        self.doctor1 = DoctorProfile.objects.create(
            doctor_name = 'Dr. John Doe',
            email = 'johndoe@example.com',
            mobile = '1234567890',
            specialization = 'Mon-Fri 9AM-5PM',
            details = 'Experienced Cardiologist',
            consulting_fee = 100.00,
            category = 'doctor'
        )

        self.doctor2 = DoctorProfile.objects.create(
            doctor_name = 'Dr. Jane Smith',
            email = 'janesmith@example.com',
            mobile = '9876543210',
            specialization = 'Geriatrics',
            schedule = 'Mon-Thu 10AM-4PM',
            details = 'Specialist in geriatric care',
            consulting_fee = 120.00,
            category = 'geriatric_counselor'
        )
    


    def test_list_all_doctors(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    
    def test_filter_doctors_by_category(self):
        response = self.client.get(self.url, {'category': 'doctor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor_name'], self.doctor1.doctor_name)


        response = self.client.get(self.url, {'category': 'geriatric_counselor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor_name'], self.doctor2.doctor_name)






class DoctorTimeSlotsViewTest(APITestCase):
    def setUp(self):
        # Create a doctor profile
        self.doctor = DoctorProfile.objects.create(
            doctor_name='Dr. Alice',
            email='alice@example.com',
            mobile='1234567890',
            specialization='Dermatology',
            schedule='Mon-Fri 9AM-5PM',
            details='Experienced dermatologist',
            consulting_fee=150.00,
            category='doctor'
        )

        # Create time slots for the doctor
        self.timeslot1 = TimeSlot.objects.create(
            day='Monday',
            start_time='09:00',
            end_time='10:00',
            doctor=self.doctor,
            is_booked=False
        )
        self.timeslot2 = TimeSlot.objects.create(
            day='Tuesday',
            start_time='11:00',
            end_time='12:00',
            doctor=self.doctor,
            is_booked=True
        )

        # Create another doctor with a different timeslot (for filtering test)
        self.other_doctor = DoctorProfile.objects.create(
            doctor_name='Dr. Bob',
            email='bob@example.com',
            mobile='0987654321',
            specialization='Cardiology',
            schedule='Mon-Fri 10AM-6PM',
            details='Expert in heart health',
            consulting_fee=200.00,
            category='doctor'
        )
        self.other_timeslot = TimeSlot.objects.create(
            day='Wednesday',
            start_time='09:00',
            end_time='10:00',
            doctor=self.other_doctor,
            is_booked=False
        )

        # Construct the URL with doctor_id for our test view
        self.url = reverse('doctor-time-slots', args=[self.doctor.id])

    def test_get_timeslots_for_specific_doctor(self):
        # Send GET request to retrieve time slots for `self.doctor`
        response = self.client.get(self.url)
        
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the length of returned timeslots to ensure only this doctor's timeslots are retrieved
        self.assertEqual(len(response.data), 2)
        
        # Verify the contents of the returned data
        timeslot_data = response.data
        self.assertEqual(timeslot_data[0]['day'], 'Monday')
        self.assertEqual(timeslot_data[0]['start_time'], '09:00:00')
        self.assertEqual(timeslot_data[0]['end_time'], '10:00:00')
        self.assertEqual(timeslot_data[0]['doctor'], self.doctor.id)
        self.assertEqual(timeslot_data[0]['doctor_name'], 'Dr. Alice')
        self.assertEqual(timeslot_data[0]['is_booked'], False)

        self.assertEqual(timeslot_data[1]['day'], 'Tuesday')
        self.assertEqual(timeslot_data[1]['start_time'], '11:00:00')
        self.assertEqual(timeslot_data[1]['end_time'], '12:00:00')
        self.assertEqual(timeslot_data[1]['doctor'], self.doctor.id)
        self.assertEqual(timeslot_data[1]['doctor_name'], 'Dr. Alice')
        self.assertEqual(timeslot_data[1]['is_booked'], True)

    def test_no_timeslots_for_invalid_doctor(self):
        # Test with a doctor ID that doesn't exist
        invalid_url = reverse('doctor-time-slots', args=[9999])
        response = self.client.get(invalid_url)
        
        # Should return an empty list
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)







class CreateAppointmentViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            password = 'testpass123',
            fullname = 'Test User',
            email = 'testuser@example.com',
            mobile = '1234567890'
        )

        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. Alice",
            email="alice@example.com",
            mobile="1234567890",
            specialization="Dermatology",
            schedule="Mon-Fri 9AM-5PM",
            details="Experienced dermatologist",
            consulting_fee=150.00,
            category="doctor"
        )


        self.time_slot = TimeSlot.objects.create(
            day = "Monday",
            start_time = "09:00",
            end_time = "10:00",
            doctor = self.doctor,
            is_booked = False
        )

        self.url = reverse('create-appointment')
    

    def test_create_appointment_success(self):
        data = {
            'user': self.user.id,
            'user_name': self.user.fullname,
            'user_email': self.user.email,
            'doctor': self.doctor.id,
            'doctor_name': self.doctor.doctor_name,
            'date': date.today().isoformat(),
            'time_slot': self.time_slot.id,
            'is_booked': True
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('appointment_id', response.data)
        self.assertEqual(response.data['details']['user'], self.user.id)
        self.assertEqual(response.data['details']['doctor'], self.doctor.id)
        self.assertEqual(response.data['details']['time_slot'], self.time_slot.id)


    
    def test_create_appointment_invalid_data(self):
        data = {
            'user': self.user.id,
            'date': date.today().isoformat(),
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('doctor', response.data)
        self.assertIn('time_slot', response.data)





class StartPaymentTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            fullname = 'Test User',
            email = 'testuser@example.com',
            mobile = '1234567890',
            password = 'password123'
        )

        self.doctor = DoctorProfile.objects.create(
            doctor_name = 'Dr. Smith',
            email = 'drsmith@example.com',
            mobile = '0987654321',
            specialization = 'Cardiology',
            consulting_fee = 500.00
        )

        self.url = reverse('payment', args=[self.user.id])

        self.payment_data = {
            'user_id': self.user.id,
            'user_name': self.user.fullname,
            'user_email': self.user.email,
            'user_mobile': self.user.mobile,
            'doctor_id': self.doctor.id,
            'doctor_name': self.doctor.doctor_name,
            'consulting_fee': '500',
            'selected_date': '2024-11-14',
            'selected_day': 'Thursday',
            'selected_start_time': '09:00:00',
            'selected_end_time': '09:30:00'
        }

    
    @patch("razorpay.Client")
    def test_start_payment_success(self, MockRazorpayClient):
        mock_payment = {
            'id': 'order_testid123',
            'amount': int(float(self.payment_data['consulting_fee']) * 100),
            'currency': 'INR'
        }
        MockRazorpayClient().order.create.return_value = mock_payment

        response = self.client.post(self.url, self.payment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('payment', response.data)
        self.assertIn('order', response.data)
        self.assertEqual(response.data['payment']['id'], mock_payment['id'])
        self.assertEqual(response.data['order']['doctor_name'], self.doctor.doctor_name)
        self.assertEqual(response.data['order']['user_name'], self.user.fullname)


        order = Order.objects.get(user=self.user, doctor=self.doctor)
        self.assertEqual(order.order_payment_id, mock_payment['id'])
        self.assertEqual(order.order_amount, self.payment_data['consulting_fee'])
        self.assertEqual(order.time_slot_date.strftime("%Y-%m-%d"), self.payment_data['selected_date'])

    

    def test_start_payment_user_not_found(self):
        invalid_data = self.payment_data.copy()
        invalid_data['user_id'] = 9999

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("User not found", str(response.data))

    

    def test_start_payment_doctor_not_found(self):
        invalid_data = self.payment_data.copy()
        invalid_data['doctor_id'] = 9999

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Doctor not found", str(response.data))




# class HandlePaymentSuccessTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             fullname = "Test User",
#             email = 'testuser@example.com',
#             mobile = '1234567890',
#             password = 'testpassword'
#         )

#         self.doctor = DoctorProfile.objects.create(
#             doctor_name = 'Dr. John Doe',
#             email = 'doctor@example.com',
#             mobile = '0987654321',
#             specialization = 'Geriatrics',
#             schedule = 'Mon-Fri, 9AM-5PM',
#             details = 'Experienced in elderly care.',
#             consulting_fee = 500.00,
#             category = 'geriatric_counselor'
#         )


#         self.timeslot = TimeSlot.objects.create(
#             doctor=self.doctor,
#             start_time=time(9, 0, 0),
#             end_time=time(10, 0, 0),
#             is_booked=False
#         )

#         # Now, create the Appointment instance and link the TimeSlot
#         self.appointment = Appointment.objects.create(
#             user=self.user,
#             doctor=self.doctor,
#             time_slot=self.timeslot,  # Assign the created TimeSlot instance
#             date=timezone.now().date(),
#             is_booked=False
#         )


#         self.order = Order.objects.create(
#             user=self.user,
#             doctor=self.doctor,
#             order_payment_id="order_123",
#             isPaid=False,
#             meet_link=None,
#             time_slot_date="2024-11-15",
#             time_slot_start_time="09:00:00"
#         )


#         self.payment_data = {
#             'razorpay_order_id': 'order_123',
#             'razorpay_payment_id': 'payment_123',
#             'razorpay_signature': 'signature_123',
#             'appointment_id': self.appointment.id,
#             'slot_id': self.timeslot.id
#         }

    

#     @patch('razorpay.Client')
#     @patch('user_side.views.create_google_meet_space')
#     def test_handle_payment_success(self, mock_create_google_meet_space, MockClient):
#         # Set up the mocks
#         mock_create_google_meet_space.return_value = "https://meet.google.com/xyz-abc-123"
#         mock_client_instance = MockClient.return_value
#         mock_client_instance.utility.verify_payment_signature.return_value = True

#         # Send the POST request to the payment success URL
#         url = reverse('payment_success')
#         response = self.client.post(url, json.dumps(self.payment_data), content_type='application/json')

#         # Assertions to verify the response and database updates
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Payment successfully received', response.json()['message'])
#         self.assertEqual(response.json()['meet_link'], "https://meet.google.com/xyz-abc-123")

#         # Refresh and verify the order, appointment, and timeslot statuses
#         self.order.refresh_from_db()
#         self.assertTrue(self.order.isPaid)
#         self.assertEqual(self.order.meet_link, 'https://meet.google.com/xyz-abc-123')

#         self.appointment.refresh_from_db()
#         self.assertTrue(self.appointment.is_booked)

#         self.timeslot.refresh_from_db()
#         self.assertTrue(self.timeslot.is_booked)

#         # Check email sent for appointment confirmation
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertIn("Appointment Confirmation", mail.outbox[0].subject)
#         self.assertIn(self.order.user.email, mail.outbox[0].to)
#         self.assertIn("Google Meet Link", mail.outbox[0].body)






# class CreateMeetViewTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = reverse('create-meet')


#     @patch('user_side.utils.create_google_meet_space')  
#     def test_create_meet_success(self, mock_create_google_meet_space):
#         # Mock the `create_google_meet_space` function to return a sample meet link
#         mock_create_google_meet_space.return_value = "https://meet.google.com/xyz-abc-123"
        
#         # Call the CreateMeetView endpoint
#         response = self.client.get(self.url)

#         # Check the response status and content
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {'meet_link': "https://meet.google.com/xyz-abc-123"})
#         mock_create_google_meet_space.assert_called_once()

#     @patch('user_side.utils.create_google_meet_space')
#     def test_create_meet_failure(self, mock_create_google_meet_space):
#         # Mock `create_google_meet_space` to return None to simulate failure
#         mock_create_google_meet_space.return_value = None

#         # Call the CreateMeetView endpoint
#         response = self.client.get(self.url)

#         # Check that the view returns a 500 error with an error message
#         self.assertEqual(response.status_code, 500)
#         self.assertEqual(response.json(), {'error': 'Failed to create Google Meet link'})
#         mock_create_google_meet_space.assert_called_once()






class UserDetailsViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            fullname = 'Test User',
            email = 'testuser@example.com',
            mobile = '1234567890',
            password = 'testpassword123',
            is_verified = True
        )
        self.url = reverse('user-details')

    
    def test_get_user_details_success(self):
        response = self.client.get(self.url, {'user_id': self.user.id})
        serializer = CustomUserSerializer(self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    
    def test_get_user_details_user_not_found(self):
        response = self.client.get(self.url, {'user_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'User not found'})


    def test_get_user_details_no_user_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User ID is required'})

    
    def test_get_user_details_internal_server_error(self):
        user_id = self.user.id
        self.user.delete()
        response = self.client.get(self.url, {'user_id': user_id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'User not found'})




class UserProfilePictureUploadTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            fullname = 'Test User',
            email = 'testuser@example.com',
            mobile = '1234567890',
            password = 'testpassword123'
        )
        self.url = reverse('upload-profile-picture', kwargs={'user_id': self.user.id})

    
    def generate_test_image(self):
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        return SimpleUploadedFile('test_image.jpg', image_file.read(), content_type='image/jpeg')
    

    def test_upload_profile_picture_success(self):
        image = self.generate_test_image()
        response = self.client.patch(self.url, {'profile_picture': image}, format='multipart')

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.user.profile_picture)
        self.assertIn('profile_picture', response.data)


    def test_upload_profile_picture_no_file_provided(self):
        response = self.client.patch(self.url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': "No profile picture provided"})




class UserAppointmentsViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            fullname = 'Test User',
            email = 'testuser@example.com',
            mobile = '1234567890',
            password = 'testpassword123'
        )
        self.url = reverse('user-appointments')

        self.order1 = Order.objects.create(
            user = self.user,
            user_name = self.user.fullname,
            user_email = self.user.email,
            doctor_name = 'Dr. Smith',
            order_amount = '100',
            order_payment_id = 'pay_001',
            isPaid = True,
            time_slot_date = '2024-12-01',
            time_slot_day = 'Monday',
            time_slot_start_time = '10:00',
            time_slot_end_time = '11:00',
            status = 'Completed'
        )

        self.order2 = Order.objects.create(
            user = self.user,
            user_name = self.user.fullname,
            user_email = self.user.email,
            doctor_name = 'Dr. Doe',
            order_amount = '150',
            order_payment_id = 'pay_002',
            isPaid = False,
            time_slot_date = '2024-12-05',
            time_slot_day = 'Friday',
            time_slot_start_time = '12:00',
            time_slot_end_time = '13:00',
            status = 'Pending'
        )


    def test_get_user_appointments_success(self):
        response = self.client.get(self.url, {'user_id': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['doctor_name'], self.order1.doctor_name)
        self.assertEqual(response.data[1]['doctor_name'], self.order2.doctor_name)

    
    def test_get_user_appointments_no_user_id(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User ID is required'})

    
    def test_get_user_appointments_no_appointments(self):
        new_user = CustomUser.objects.create(
            fullname = 'New User',
            email = 'newuser@example.com',
            mobile = '0987654321',
            password = 'newpassword123'
        )
        response = self.client.get(self.url, {'user_id': new_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)





class UserAssessmentHistoryViewTests(APITestCase):
    def setUp(self):
        # Create a user and their assessment records
        self.user = CustomUser.objects.create(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            password="testpassword"
        )

        # Create sample assessment records for the user
        self.assessment1 = FirstPersonClientDetails.objects.create(
            fullname="John Doe",
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            age="30",
            assessment_score=85,
            interpretation="Mild",
            assessment_date=datetime.now()
        )
        
        self.assessment2 = FirstPersonClientDetails.objects.create(
            fullname="John Doe",
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            age="30",
            assessment_score=90,
            interpretation="Moderate",
            assessment_date=datetime.now()
        )
        
        # URL for the view
        self.url = reverse('assessments')

    def test_get_assessment_history_success(self):
        # Test for successful retrieval of assessments with user_id
        response = self.client.get(self.url, {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ensure response contains the assessment history
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user_name'], "John Doe")
        self.assertEqual(response.data[1]['assessment_score'], 90)

    def test_get_assessment_history_no_user_id(self):
        # Test when user_id is not provided in the request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User ID is required'})

    def test_get_assessment_history_invalid_user_id(self):
        # Test when an invalid user_id is provided
        response = self.client.get(self.url, {'user_id': 9999})  # Assuming 9999 does not exist
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Expecting an empty list for non-existent user

    def test_get_assessment_history_server_error(self):
        # Test for handling server errors (mock an error if needed)
        with self.assertRaises(Exception):
            response = self.client.get(self.url, {'user_id': None})  # Invalid user_id to trigger an error
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)





class FirstPersonClientDetailsViewTests(APITestCase):
    def setUp(self):
        # URL for the view
        self.url = reverse('first-person-client-details')

    def test_create_first_person_client_success(self):
        # Test successful creation of a client detail
        data = {
            'name': 'Alice Johnson',
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response status code and data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Client details saved successfully")
        self.assertEqual(response.data['fullname'], "Alice Johnson")
        
        # Verify the record was created in the database
        client = FirstPersonClientDetails.objects.get(id=response.data['id'])
        self.assertEqual(client.fullname, "Alice Johnson")
        self.assertEqual(client.assessment_date, datetime.now().date())

    def test_create_first_person_client_missing_name(self):
        # Test the response when 'name' is missing or empty
        data = {'name': ''}
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Name is required')

    def test_create_first_person_client_whitespace_name(self):
        # Test the response when 'name' is only whitespace
        data = {'name': '   '}
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Name is required')





class SendAssessmentEmailViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('send-first-person-assessment-email')
        self.valid_data = {
            'email': 'user@example.com',
            'fullname': 'Alice Johnson',
            'score': 85,
            'interpretation': 'Mild cognitive impairment'
        }

    @patch('user_side.views.send_mail')
    def test_send_assessment_email_success(self, mock_send_mail):
        # Mock the send_mail function to simulate successful email sending
        mock_send_mail.return_value = 1

        response = self.client.post(self.url, self.valid_data, format='json')

        # Check response status code and message
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Email sent successfully')

        # Verify that send_mail was called with the correct parameters
        mock_send_mail.assert_called_once_with(
            'Your Assessment Results',
            'Hello Alice Johnson, \n\nYour assessment is complete. \n\nScore: 85\nInterpretation: Mild cognitive impairment\n\nThank you for completing assessment!',
            'support.easedementia@gmail.com',
            ['user@example.com']
        )

    def test_send_assessment_email_missing_field(self):
        # Test the response when a required field (e.g., 'email') is missing
        invalid_data = self.valid_data.copy()
        invalid_data.pop('email')  # Remove email to test missing field

        response = self.client.post(self.url, invalid_data, format='json')

        # Check response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    @patch('user_side.views.send_mail')
    def test_send_assessment_email_failure(self, mock_send_mail):
        # Simulate an exception in send_mail to test error handling
        mock_send_mail.side_effect = Exception("Failed to send email")

        response = self.client.post(self.url, self.valid_data, format='json')

        # Check response status code and error message
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()['error'], 'Failed to send email')







class UpdateAssessmentScoreAPIViewTests(APITestCase):
    
    def setUp(self):
        # Create sample user and client details
        self.user = CustomUser.objects.create(fullname="Test User", email="user@example.com")
        self.client_details = FirstPersonClientDetails.objects.create(fullname="Client Test", user=self.user)
        self.update_score_url = reverse('update-assessment-score')


    def test_post_update_score_success(self):
        """Test POST request for updating score and interpretation successfully"""
        data = {
            "clientId": self.client_details.id,
            "score": 85,
            "interpretation": "Good progress"
        }
        response = self.client.post(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Score and interpretation updated successfully')
        self.client_details.refresh_from_db()
        self.assertEqual(self.client_details.assessment_score, 85)
        self.assertEqual(self.client_details.interpretation, "Good progress")


    def test_post_update_score_client_not_found(self):
        """Test POST request for updating score when clientId does not exist"""
        data = {
            "clientId": 9999,  # Invalid ID
            "score": 85,
            "interpretation": "Good progress"
        }
        response = self.client.post(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Client not found')


    def test_post_update_score_missing_field(self):
        """Test POST request with missing fields to ensure 400 response"""
        data = {
            "clientId": self.client_details.id,
            "score": 85  # Missing interpretation
        }
        response = self.client.post(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_put_update_user_success(self):
        """Test PUT request for updating user successfully"""
        new_user = CustomUser.objects.create(fullname="New User", email="newuser@example.com")
        data = {
            "clientId": self.client_details.id,
            "user": new_user.id
        }
        response = self.client.put(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully')
        self.client_details.refresh_from_db()
        self.assertEqual(self.client_details.user, new_user)


    def test_put_update_user_client_not_found(self):
        """Test PUT request for updating user when clientId does not exist"""
        new_user = CustomUser.objects.create(fullname="New User", email="newuser@example.com")
        data = {
            "clientId": 9999,  # Invalid clientId
            "user": new_user.id
        }
        response = self.client.put(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Client not found')


    def test_put_update_user_user_not_found(self):
        """Test PUT request for updating user when user ID does not exist"""
        data = {
            "clientId": self.client_details.id,
            "user": 9999  # Invalid user ID
        }
        response = self.client.put(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')


    def test_put_update_user_missing_user_id(self):
        """Test PUT request with missing user ID to ensure 400 response"""
        data = {
            "clientId": self.client_details.id
            # Missing 'user' field
        }
        response = self.client.put(self.update_score_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User ID is required')



        


class UpdateUserDetailsTestCase(TestCase):
    def setUp(self):
        # Set up test data
        self.user = CustomUser.objects.create_user(
            fullname="Test User",
            email="testuser@example.com",
            password="password123",
            mobile = '1234567890'
        )
        self.client_details = FirstPersonClientDetails.objects.create(
            fullname="John Doe",
            user=self.user,
            user_name="john_doe",
            user_email="johndoe@example.com",
            age="30",
            assessment_score=85,
            interpretation="Mild Cognitive Impairment",
        )
        self.client = APIClient()
        self.url = f'/update-first-person-user-details/{self.client_details.id}/'
        self.valid_payload = {
            'fullname': 'John Updated',
            'age': '31',
        }
        self.invalid_payload = {
            'assessment_score': 'invalid_score',  # Invalid data type
        }

    def test_update_user_details_success(self):
        """Test updating user details with valid payload"""
        response = self.client.put(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User details updated successfully')
        
        # Verify the changes in the database
        self.client_details.refresh_from_db()
        self.assertEqual(self.client_details.fullname, 'John Updated')
        self.assertEqual(self.client_details.age, '31')

    def test_update_user_details_not_found(self):
        """Test updating user details for a non-existent client"""
        url = '/update-first-person-user-details/9999/'  # Non-existent ID
        response = self.client.put(url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Client not found')

    def test_update_user_details_invalid_data(self):
        """Test updating user details with invalid payload"""
        response = self.client.put(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assessment_score', response.data)






class CheckUserEmailTests(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = CustomUser.objects.create(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            password="testpassword"
        )
        self.valid_email = self.user.email
        self.invalid_email = "nonexistent@example.com"

    def test_email_exists(self):
        url = reverse('check-user-email')
        data = {'email': self.valid_email}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exists', response.data)
        self.assertTrue(response.data['exists'])

    def test_email_does_not_exist(self):
        url = reverse('check-user-email')
        data = {'email': self.invalid_email}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exists', response.data)
        self.assertFalse(response.data['exists'])

    def test_email_field_missing(self):
        url = reverse('check-user-email')
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')





class RegisterNewUserViewTests(APITestCase):

    def setUp(self):
        # Define the URL for the endpoint
        self.url = reverse('register-new-user')
        # Valid user data
        self.valid_user_data = {
            "fullname": "Jane Doe",
            "email": "janedoe@example.com",
            "mobile": "9876543210",
            "password": "securepassword"
        }
        # Missing fields
        self.missing_field_data = {
            "fullname": "Jane Doe",
            "email": "janedoe@example.com"
        }
        # Invalid data (duplicate email)
        self.duplicate_email_data = {
            "fullname": "John Smith",
            "email": "janedoe@example.com",
            "mobile": "1234567890",
            "password": "anotherpassword"
        }

    def test_register_new_user_success(self):
        """Test registering a new user with valid data."""
        response = self.client.post(self.url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User registered successfully')

        # Ensure the user is created in the database
        user = CustomUser.objects.filter(email=self.valid_user_data['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.fullname, self.valid_user_data['fullname'])
        self.assertEqual(user.mobile, self.valid_user_data['mobile'])

    def test_register_new_user_missing_field(self):
        """Test registering a user with missing fields."""
        response = self.client.post(self.url, self.missing_field_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_new_user_duplicate_email(self):
        """Test registering a user with a duplicate email."""
        # Create a user with the email
        CustomUser.objects.create(
            fullname="Existing User",
            email=self.valid_user_data['email'],
            mobile="1111111111",
            password="password"
        )

        response = self.client.post(self.url, self.duplicate_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_new_user_no_data(self):
        """Test registering a user with no data."""
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)





class SubscribeNewsLetterTests(APITestCase):

    def setUp(self):
        # Define the endpoint URL
        self.url = reverse('subscribe-newsletter')

        # Test data
        self.valid_email_data = {'email': 'testuser@example.com'}
        self.invalid_email_data = {'email': ''}
        self.duplicate_email_data = {'email': 'existinguser@example.com'}

        # Create a subscription for duplicate email test
        NewsLetterSubscription.objects.create(email='existinguser@example.com')

    def test_subscribe_newsletter_success(self):
        """Test subscribing to the newsletter with a valid email."""
        response = self.client.post(self.url, self.valid_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Successfully subscribed')

        # Verify the subscription was created in the database
        subscription = NewsLetterSubscription.objects.filter(email=self.valid_email_data['email']).first()
        self.assertIsNotNone(subscription)

    def test_subscribe_newsletter_missing_email(self):
        """Test subscribing to the newsletter without providing an email."""
        response = self.client.post(self.url, self.invalid_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')

    def test_subscribe_newsletter_duplicate_email(self):
        """Test subscribing to the newsletter with an already subscribed email."""
        response = self.client.post(self.url, self.duplicate_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Already subscribed')

    def test_subscribe_newsletter_server_error(self):
        """Test server error scenario."""
        with self.assertRaises(Exception):
            # Simulate an unexpected error
            with self.settings(DEBUG_PROPAGATE_EXCEPTIONS=False):
                response = self.client.post(self.url, {}, format='json')
                self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)