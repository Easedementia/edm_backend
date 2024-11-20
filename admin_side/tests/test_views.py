from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from user_side.models import *
from admin_side.models import *
from django.test import TestCase
from django.urls import reverse
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import tempfile
from datetime import time





class AdminLoginViewTest(TestCase):
    
    def setUp(self):
        # Create a user that can log in as an admin
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com",
            password="adminpassword",  # This will hash the password
            fullname="Admin User",
            mobile="1234567890",
            is_staff=True
        )
        # Create a non-admin user for negative test
        self.non_admin_user = CustomUser.objects.create_user(
            email="user@example.com",
            password="userpassword",  # This will hash the password
            fullname="Normal User",
            mobile="0987654321",
            is_staff=False
        )
        
        self.client = APIClient()

    def test_admin_login_success(self):
        # Prepare login data
        data = {
            'email': 'admin@example.com',
            'password': 'adminpassword'
        }
        
        # Make a POST request to login
        response = self.client.post('/admin-side/admin-login/', data, format='json')
        
        # Check if response status is 200 OK and check the tokens in the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'admin@example.com')
        self.assertEqual(response.data['user']['fullname'], 'Admin User')

    def test_admin_login_invalid_credentials(self):
        # Invalid credentials (wrong password)
        data = {
            'email': 'admin@example.com',
            'password': 'wrongpassword'
        }
        
        # Make a POST request to login
        response = self.client.post('/admin-side/admin-login/', data, format='json')
        
        # Check if response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_non_admin_login(self):
        # Non-admin user login attempt
        data = {
            'email': 'user@example.com',
            'password': 'userpassword'
        }
        
        # Make a POST request to login
        response = self.client.post('/admin-side/admin-login/', data, format='json')
        
        # Check if response status is 401 Unauthorized since the user is not an admin
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)





class UserListViewTest(TestCase):
    
    def setUp(self):
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com",
            password="adminpassword",
            fullname="User One",
            mobile="1234567890",
            is_staff=True
        )
        self.non_admin_user = CustomUser.objects.create_user(
            email="user@example.com",
            password="userpassword",
            fullname="User Two",
            mobile="0987654321",
            is_staff=False
        )
        
        self.client = APIClient()

    def test_user_list(self):
        # Make a GET request to the user list endpoint
        response = self.client.get('/admin-side/user-list/', format='json')

        # Check if response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains both users
        self.assertEqual(len(response.data), 2)
        
        # Check the fields in the response for each user
        user1_data = response.data[0]
        self.assertEqual(user1_data['fullname'], 'User One')
        self.assertEqual(user1_data['email'], 'admin@example.com')  # Updated based on setUp
        self.assertEqual(user1_data['mobile'], '1234567890')
        self.assertEqual(user1_data['is_active'], True)

        user2_data = response.data[1]
        self.assertEqual(user2_data['fullname'], 'User Two')
        self.assertEqual(user2_data['email'], 'user@example.com')
        self.assertEqual(user2_data['mobile'], '0987654321')
        self.assertEqual(user2_data['is_active'], True)

    def test_user_list_no_users(self):
        # Delete all users for this test
        CustomUser.objects.all().delete()

        # Make a GET request to the user list endpoint
        response = self.client.get('/admin-side/user-list/', format='json')

        # Check if response status is 200 OK and an empty list is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)





class UserUpdateViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            email = 'testuser@example.com',
            fullname = 'Test User',
            mobile = '1234567890',
            password = 'password123',
            is_blocked = False
        )
        self.url = reverse('user-update', kwargs={'email': self.user.email})

    
    def test_update_user_is_blocked_status(self):
        response = self.client.patch(self.url, {'is_blocked': True}, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_blocked)
        self.assertEqual(response.data, {'status': 'success'})


    def test_update_user_not_found(self):
        non_existent_url = reverse('user-update', kwargs={'email': 'nonexistent@example.com'})
        response = self.client.patch(non_existent_url, {'is_blocked': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'User not found'})

    
    def test_update_user_no_changes(self):
        response = self.client.patch(self.url, {}, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.is_blocked)
        self.assertEqual(response.data, {'status': 'success'})



class AddServiceViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('add-service')

    
    def test_add_service_success(self):
        valid_svg_content = b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>'
        valid_image = SimpleUploadedFile("test_image.svg", valid_svg_content, content_type="image/svg+xml")

        data = {
            'title': 'Test Service',
            'description': 'This is a test service description.',
            'image': valid_image
        }
        response = self.client.post(self.url, data, format='multipart')


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)
        service = Service.objects.first()
        self.assertEqual(service.title, 'Test Service')
        self.assertEqual(service.description, 'This is a test service description.')

    
    def test_add_service_invalid_image(self):
        invalid_image_content = b'Not an SVG content'
        invalid_image = SimpleUploadedFile("test_image.png", invalid_image_content, content_type="image/png")

        data = {
            'title': 'Test Service',
            'description': 'This is a test service description.',
            'image': invalid_image
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)


    def test_add_service_missing_fields(self):
        data = {
            'title': '',
            'description': 'This service has no title.',
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('image', response.data)






class ServiceListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('service-list')

    def test_get_services_empty(self):
        # Test GET method when no services exist
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Should return an empty list

    def test_get_services_with_data(self):
        # Add test data
        Service.objects.create(title="Test Service 1", description="Description 1")
        Service.objects.create(title="Test Service 2", description="Description 2")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], "Test Service 1")
        self.assertEqual(response.data[1]['title'], "Test Service 2")

    def test_post_service_success(self):
        # Prepare valid service data
        valid_svg_content = b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>'
        valid_image = SimpleUploadedFile("test_image.svg", valid_svg_content, content_type="image/svg+xml")

        data = {
            "title": "New Service",
            "description": "A new service description.",
            "image": valid_image,
        }
        response = self.client.post(self.url, data, format='multipart')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)
        service = Service.objects.first()
        self.assertEqual(service.title, "New Service")
        self.assertEqual(service.description, "A new service description.")

    def test_post_service_invalid_data(self):
        # Test POST method with missing required fields
        data = {
            "title": "",
            "description": "Missing title and image",
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)  # Check for title validation error
        self.assertIn('image', response.data)




class ServiceDetailViewTest(APITestCase):
    def setUp(self):
        # Create a test service
        valid_svg_content = b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>'
        valid_image = SimpleUploadedFile("test_image.svg", valid_svg_content, content_type="image/svg+xml")

        self.service = Service.objects.create(
            title="Test Service",
            description="Test service description",
            image=valid_image
        )
        self.detail_url = reverse('service-detail', kwargs={'pk': self.service.pk})

    def test_get_service_success(self):
        # Test GET method
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.service.title)
        self.assertEqual(response.data['description'], self.service.description)

    def test_get_service_not_found(self):
        # Test GET method with invalid pk
        invalid_url = reverse('service-detail', kwargs={'pk': 999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_service_success(self):
        # Test PUT method
        updated_data = {
            "title": "Updated Service Title",
            "description": "Updated service description",
        }
        response = self.client.put(self.detail_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, updated_data['title'])
        self.assertEqual(self.service.description, updated_data['description'])

    def test_put_service_invalid_data(self):
        # Test PUT method with invalid data
        invalid_data = {"title": ""}
        response = self.client.put(self.detail_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_delete_service_success(self):
        # Test DELETE method
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Service.objects.filter(pk=self.service.pk).exists())

    def test_delete_service_not_found(self):
        # Test DELETE method with invalid pk
        invalid_url = reverse('service-detail', kwargs={'pk': 999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


def create_test_image():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        image = Image.new("RGB", (100, 100), color="white")
        image.save(tmp, format="JPEG")
        tmp.seek(0)
        return SimpleUploadedFile(
            tmp.name, tmp.read(), content_type="image/jpeg"
        )

class DoctorProfileCreateViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('doctor-creation')
        self.valid_data = {
            "doctor_name": "Dr. John Doe",
            "email": "john.doe@example.com",
            "mobile": "1234567890",
            "specialization": "Cardiology",
            "schedule": "Mon-Fri 10am-3pm",
            "details": "Experienced cardiologist with over 10 years of practice.",
            "consulting_fee": "150.00",
            "profile_picture": create_test_image(),
            "category": "doctor"
        }
        self.invalid_data = {
            "doctor_name": "",  # Missing name
            "email": "invalid-email",  # Invalid email
            "mobile": "invalid-phone",  # Invalid phone
            "specialization": "Cardiology",
            "schedule": "Mon-Fri 10am-3pm",
            "details": "Experienced cardiologist with over 10 years of practice.",
            "consulting_fee": "150.00",
            "category": "doctor"
        }
        

    def test_create_doctor_success(self):
        response = self.client.post(self.url, self.valid_data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)  # Debug validation errors
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorProfile.objects.count(), 1)
        doctor = DoctorProfile.objects.first()
        self.assertEqual(doctor.doctor_name, self.valid_data["doctor_name"])


    def test_create_doctor_invalid_data(self):
        # Test creation of a doctor profile with invalid data
        response = self.client.post(self.url, self.invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DoctorProfile.objects.count(), 0)
        self.assertIn('doctor_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('profile_picture', response.data)  # Include required fields in checks
        # Check for mobile only if it's required in the serializer
        if 'mobile' in response.data:
            self.assertIn('mobile', response.data)


    def test_create_doctor_duplicate_email(self):
        # Test creation of a doctor profile with a duplicate email
        DoctorProfile.objects.create(
            doctor_name="Dr. Jane Doe",
            email=self.valid_data['email'],  # Duplicate email
            mobile="9876543210",
            specialization="Neurology",
            schedule="Mon-Fri 11am-4pm",
            details="Experienced neurologist.",
            consulting_fee="200.00",
            profile_picture=SimpleUploadedFile(
                "profile_picture.jpg",
                b"file_content",
                content_type="image/jpeg"
            ),
            category="doctor"
        )
        response = self.client.post(self.url, self.valid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(DoctorProfile.objects.count(), 1)






class DoctorProfileListViewTest(APITestCase):
    def setUp(self):
        # Create a test doctor profile
        self.url = reverse('admin-doctors-list')  # URL for the list view
        self.doctor_data = {
            "doctor_name": "Dr. John Doe",
            "email": "john.doe@example.com",
            "mobile": "1234567890",
            "specialization": "Cardiology",
            "schedule": "Mon-Fri, 9 AM - 5 PM",
            "details": "Experienced cardiologist with 10+ years in practice.",
            "consulting_fee": "100.00",
            "profile_picture": None,  # Assuming you don't want to test image upload here
            "category": "doctor"
        }
        self.client = APIClient()
        # Create doctor profile
        DoctorProfile.objects.create(**self.doctor_data)

    def test_doctor_profile_list_success(self):
        # Send a GET request to the doctors list URL
        response = self.client.get(self.url)
        
        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the returned data contains the doctor data
        self.assertEqual(len(response.data), 1)  # Only one doctor should be in the list
        self.assertEqual(response.data[0]['doctor_name'], self.doctor_data['doctor_name'])
        self.assertEqual(response.data[0]['email'], self.doctor_data['email'])
        self.assertEqual(response.data[0]['specialization'], self.doctor_data['specialization'])
        self.assertEqual(response.data[0]['schedule'], self.doctor_data['schedule'])

    def test_doctor_profile_list_empty(self):
        # Delete all doctor profiles to test empty response
        DoctorProfile.objects.all().delete()

        # Send a GET request to the doctors list URL
        response = self.client.get(self.url)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the returned data is an empty list
        self.assertEqual(response.data, [])





class DoctorProfileDetailViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test doctor profile
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="john.doe@example.com",
            mobile="1234567890",
            specialization="Cardiology",
            schedule="Mon-Fri, 9 AM - 5 PM",
            details="Experienced cardiologist with 10+ years in practice.",
            consulting_fee="100.00",
            profile_picture=None,  # Test with no profile picture
            category="doctor"
        )
        self.valid_url = reverse('doctors-details', kwargs={'id': self.doctor.id})
        self.invalid_url = reverse('doctors-details', kwargs={'id': 9999})  # Invalid ID

        self.valid_update_data = {
            "doctor_name": "Dr. Jane Doe",
            "email": "jane.doe@example.com",
            "mobile": "9876543210",
            "specialization": "Neurology",
            "schedule": "Tue-Sat, 10 AM - 4 PM",
            "details": "Expert neurologist with extensive experience.",
            "consulting_fee": "120.00",
            "category": "doctor"
        }

        self.invalid_update_data = {
            "email": "not-a-valid-email",  # Invalid email format
            "consulting_fee": "-50.00"  # Negative consulting fee
        }

    def test_get_doctor_success(self):
        # Send a GET request to retrieve the doctor
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor_name'], self.doctor.doctor_name)

    def test_get_doctor_not_found(self):
        # Send a GET request with an invalid ID
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_doctor_success(self):
        # Send a PUT request to update the doctor's details
        response = self.client.put(self.valid_url, self.valid_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor_name'], self.valid_update_data['doctor_name'])
        self.assertEqual(response.data['email'], self.valid_update_data['email'])

    def test_update_doctor_not_found(self):
        # Send a PUT request with an invalid ID
        response = self.client.put(self.invalid_url, self.valid_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_update_doctor_invalid_data(self):
        invalid_update_data = {
            "doctor_name": "Dr. Jane Doe",
            "email": "jane.doe@example.com",
            "mobile": "9876543210",
            "specialization": "Neurology",
            "schedule": "Tue-Sat, 10 AM - 4 PM",
            "details": "Expert neurologist with extensive experience.",
            "consulting_fee": "-50.00",  # Invalid consulting_fee
            "profile_picture": create_test_image(),  # Valid image file
            "category": "doctor"
        }
        
        # Send a PUT request with invalid consulting_fee
        response = self.client.put(self.valid_url, invalid_update_data, format='multipart')
        
        # Validate response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('consulting_fee', response.data)





class TimeSlotCreateViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a doctor profile for testing
        cls.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. Test",
            email="dr.test@example.com",
            mobile="1234567890",
            specialization="General Medicine",
            schedule="Mon-Fri",
            details="Experienced General Practitioner",
            consulting_fee="200.00",
            category="doctor"
        )
        # Valid timeslot data
        cls.valid_timeslot_data = {
            "day": "Monday",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "doctor": cls.doctor.id,
            "is_booked": False
        }
        # Invalid timeslot data (overlapping time slot)
        cls.invalid_timeslot_data = {
            "day": "Monday",
            "start_time": "09:30:00",
            "end_time": "10:30:00",
            "doctor": cls.doctor.id,
            "is_booked": False
        }


    def test_get_timeslots(self):
        # Create a sample time slot
        TimeSlot.objects.create(
            day="Monday",
            start_time=time(9, 0),  # Use naive time
            end_time=time(10, 0),  # Use naive time
            doctor=self.doctor
        )

        # Send GET request
        response = self.client.get("/admin-side/add-timeslots/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['day'], "Monday")




    def test_create_timeslot_success(self):
        # Send POST request with valid data
        response = self.client.post("/admin-side/add-timeslots/", self.valid_timeslot_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['day'], self.valid_timeslot_data['day'])
        self.assertEqual(response.data['doctor'], self.valid_timeslot_data['doctor'])


    def test_create_timeslot_overlap(self):
        # Create an initial time slot
        TimeSlot.objects.create(
            day="Monday",
            start_time=time(9, 0),  # Use naive time
            end_time=time(10, 0),  # Use naive time
            doctor=self.doctor
        )

        # Send POST request with overlapping time slot
        self.invalid_timeslot_data = {
            'day': 'Monday',
            'start_time': '09:30:00',  # Overlaps with the existing slot
            'end_time': '10:30:00',
            'doctor': self.doctor.id
        }
        response = self.client.post("/admin-side/add-timeslots/", self.invalid_timeslot_data, format='json')

        # Assert the response status and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn("Time slot overlaps with another time slot.", response.data['non_field_errors'][0])



    def test_create_timeslot_invalid_times(self):
        invalid_time_data = self.valid_timeslot_data.copy()
        invalid_time_data['start_time'] = "10:00:00"
        invalid_time_data['end_time'] = "09:00:00"  # End time before start time

        # Send POST request with invalid time data
        response = self.client.post("/admin-side/add-timeslots/", invalid_time_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn("Start time must be before end time.", response.data['non_field_errors'][0])






class TimeSlotListViewTest(APITestCase):
    def setUp(self):
        # Create a doctor
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="john.doe@example.com",
            mobile="1234567890",
            specialization="General Medicine",
            consulting_fee=500
        )

        # Create a few time slots
        TimeSlot.objects.create(
            day="Monday",
            start_time=time(9, 0),
            end_time=time(10, 0),
            doctor=self.doctor
        )
        TimeSlot.objects.create(
            day="Tuesday",
            start_time=time(11, 0),
            end_time=time(12, 0),
            doctor=self.doctor
        )

    def test_get_timeslots_list(self):
        # Send GET request to the timeslots-list endpoint
        response = self.client.get("/admin-side/timeslots-list/")

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the number of time slots returned
        self.assertEqual(len(response.data), 2)

        # Assert the details of the first time slot
        self.assertEqual(response.data[0]['day'], "Monday")
        self.assertEqual(response.data[0]['start_time'], "09:00:00")
        self.assertEqual(response.data[0]['end_time'], "10:00:00")
        self.assertEqual(response.data[0]['doctor'], self.doctor.id)

        # Assert the details of the second time slot
        self.assertEqual(response.data[1]['day'], "Tuesday")
        self.assertEqual(response.data[1]['start_time'], "11:00:00")
        self.assertEqual(response.data[1]['end_time'], "12:00:00")
        self.assertEqual(response.data[1]['doctor'], self.doctor.id)






class AppointmentListViewTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="password123",
            fullname="Test User",
            mobile="9876543210"
        )

        # Create a doctor profile
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            specialization="Cardiology",
            consulting_fee=500
        )

        # Create a few orders
        Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="500",
            order_payment_id="PAY12345",
            isPaid=True,
            time_slot_date="2024-11-20",
            time_slot_day="Monday",
            time_slot_start_time="09:00:00",
            time_slot_end_time="10:00:00",
            meet_link="https://meet.google.com/test-link",
            status="Completed"
        )

        Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="700",
            order_payment_id="PAY67890",
            isPaid=False,
            time_slot_date="2024-11-21",
            time_slot_day="Tuesday",
            time_slot_start_time="11:00:00",
            time_slot_end_time="12:00:00",
            meet_link=None,
            status="Pending"
        )

    def test_get_appointments_list(self):
        # Send GET request to the appointments-list endpoint
        response = self.client.get("/admin-side/appointments-list/")

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the number of orders returned
        self.assertEqual(len(response.data), 2)

        # Assert the details of the first order
        self.assertEqual(response.data[0]['user_name'], "Test User")
        self.assertEqual(response.data[0]['doctor_name'], "Dr. John Doe")
        self.assertEqual(response.data[0]['order_amount'], "500")
        self.assertEqual(response.data[0]['status'], "Completed")
        self.assertEqual(response.data[0]['meet_link'], "https://meet.google.com/test-link")

        # Assert the details of the second order
        self.assertEqual(response.data[1]['user_name'], "Test User")
        self.assertEqual(response.data[1]['doctor_name'], "Dr. John Doe")
        self.assertEqual(response.data[1]['order_amount'], "700")
        self.assertEqual(response.data[1]['status'], "Pending")
        self.assertIsNone(response.data[1]['meet_link'])





class UpdateAppointmentStatusViewTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="password123",
            fullname="Test User",
            mobile="9876543210"
        )

        # Create a doctor profile
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            specialization="Cardiology",
            consulting_fee=500
        )

        # Create an appointment (order)
        self.appointment = Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="500",
            order_payment_id="PAY12345",
            isPaid=True,
            time_slot_date="2024-11-20",
            time_slot_day="Monday",
            time_slot_start_time="09:00:00",
            time_slot_end_time="10:00:00",
            meet_link="https://meet.google.com/test-link",
            status="Pending"
        )

    def test_update_appointment_status_success(self):
        # Send PUT request to update the appointment status
        url = f"/admin-side/update-appointment-status/{self.appointment.id}"
        data = {"status": "Completed"}
        response = self.client.put(url, data, format='json')

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Status updated successfully')

        # Refresh the appointment from the database and check the status
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "Completed")

    def test_update_appointment_status_invalid_status(self):
        # Send PUT request with an invalid status
        url = f"/admin-side/update-appointment-status/{self.appointment.id}"
        data = {"status": "InvalidStatus"}
        response = self.client.put(url, data, format='json')

        # Assert the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid status')

        # Ensure the appointment status has not changed
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "Pending")

    def test_update_appointment_status_not_found(self):
        # Send PUT request for a non-existent appointment
        url = "/admin-side/update-appointment-status/99999"
        data = {"status": "Completed"}
        response = self.client.put(url, data, format='json')

        # Assert the response status code is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Appointment not found')