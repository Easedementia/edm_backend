from django.test import TestCase
from user_side.models import *
from django.core.exceptions import ValidationError
from datetime import date, time




class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            password="securepassword123"
        )

    def test_user_creation(self):
        """Test that the user is created successfully"""
        user = self.user
        self.assertEqual(user.fullname, "John Doe")
        self.assertEqual(user.email, "johndoe@example.com")
        self.assertTrue(user.check_password("securepassword123"))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_user_string_representation(self):
        """Test the string representation of the user"""
        self.assertEqual(str(self.user), "John Doe")

    def test_user_groups_permissions(self):
        """Test that the user has no groups or permissions by default"""
        self.assertEqual(self.user.groups.count(), 0)
        self.assertEqual(self.user.user_permissions.count(), 0)

    def test_user_profile_picture_null_by_default(self):
        """Test that the profile picture is null by default"""
        self.assertFalse(self.user.profile_picture)

    def test_user_otp_default(self):
        """Test that OTP is null by default"""
        self.assertIsNone(self.user.otp)

    def test_user_verification_status(self):
        """Test that the user is not verified by default"""
        self.assertFalse(self.user.is_verified)

    def test_blocked_status_default(self):
        """Test that the user is not blocked by default"""
        self.assertFalse(self.user.is_blocked)




class EnquiriesModelTest(TestCase):
    def setUp(self):
        """Set up a sample enquiry object."""
        self.enquiry = Enquiries.objects.create(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            message="This is a test enquiry."
        )

    def test_enquiry_creation(self):
        """Test that the enquiry is created successfully."""
        enquiry = self.enquiry
        self.assertEqual(enquiry.fullname, "John Doe")
        self.assertEqual(enquiry.email, "johndoe@example.com")
        self.assertEqual(enquiry.mobile, "1234567890")
        self.assertEqual(enquiry.message, "This is a test enquiry.")

    def test_string_representation(self):
        """Test the string representation of the enquiry."""
        self.assertEqual(str(self.enquiry), "John Doe")

    def test_field_lengths(self):
        # Exceeding the maximum length of fullname
        enquiry = Enquiries(
            fullname="J" * 256,  # Max length is 255
            email="test@example.com",
            mobile="1234567890",
            message="Testing max length."
        )
        with self.assertRaises(Exception):
            enquiry.full_clean()

        # Exceeding the maximum length of mobile
        enquiry = Enquiries(
            fullname="Jane Doe",
            email="test@example.com",
            mobile="1" * 16,  # Max length is 15
            message="Testing max length."
        )
        with self.assertRaises(Exception):
            enquiry.full_clean()


    def test_blank_message(self):
        enquiry = Enquiries(
            fullname="Jane Doe",
            email="janedoe@example.com",
            mobile="9876543210",
            message=""  # Blank message
        )
        with self.assertRaises(ValidationError):
            enquiry.full_clean()  # Validate the model instance





class AppointmentModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            password="testpassword123"
        )
        
        # Create a test doctor
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. Smith",
            email="drsmith@example.com",
            mobile="9876543210",
            specialization="Cardiology",
            consulting_fee=500,
            category="doctor"
        )
        
        # Create a test time slot
        self.time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            day="Monday",
            start_time=time(10, 0),
            end_time=time(11, 0),
            is_booked=False
        )
    
    def test_appointment_creation(self):
        """Test creating an appointment instance"""
        appointment = Appointment.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            date=date.today(),
            time_slot=self.time_slot,
            is_booked=True
        )
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertTrue(appointment.is_booked)
    
    def test_default_is_booked(self):
        """Test that is_booked is False by default"""
        appointment = Appointment.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            date=date.today(),
            time_slot=self.time_slot
        )
        self.assertFalse(appointment.is_booked)

    def test_appointment_str_representation(self):
        """Test the string representation of an appointment"""
        appointment = Appointment.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            date=date.today(),
            time_slot=self.time_slot
        )
        self.assertEqual(
            str(appointment),
            f"{self.user} - {self.doctor} - {appointment.date}"
        )





class OrderModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            fullname="Jane Doe",
            email="janedoe@example.com",
            mobile="1234567890",
            password="securepassword123"
        )

        # Create a test doctor
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. Alice",
            email="dralice@example.com",
            mobile="9876543210",
            specialization="Dermatology",
            consulting_fee=600,
            category="doctor"
        )

        # Create a test order
        self.order = Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="1000",
            order_payment_id="PAY123456789",
            isPaid=True,
            time_slot_date=date.today(),
            time_slot_day="Monday",
            time_slot_start_time=time(9, 0),
            time_slot_end_time=time(10, 0),
            meet_link="https://meet.google.com/test-link",
            status="Completed"
        )

    def test_order_creation(self):
        """Test that an order instance is created successfully."""
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.doctor, self.doctor)
        self.assertTrue(self.order.isPaid)
        self.assertEqual(self.order.status, "Completed")
        self.assertEqual(self.order.meet_link, "https://meet.google.com/test-link")

    def test_default_status(self):
        """Test that the default status is 'Pending'."""
        order = Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="800",
            order_payment_id="PAY987654321"
        )
        self.assertEqual(order.status, "Pending")

    def test_blank_meet_link(self):
        """Test that the meet link can be blank."""
        order = Order.objects.create(
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            doctor=self.doctor,
            doctor_name=self.doctor.doctor_name,
            order_amount="500",
            order_payment_id="PAY1122334455"
        )
        self.assertIsNone(order.meet_link)

    def test_str_representation(self):
        """Test the string representation of the order."""
        self.assertEqual(
            str(self.order),
            f"Order {self.order.id} by {self.order.user_name} for {self.order.doctor_name}"
        )





class FirstPersonClientDetailsModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            fullname="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            password="password123"
        )

        # Create a FirstPersonClientDetails instance
        self.client_details = FirstPersonClientDetails.objects.create(
            fullname="Jane Doe",
            user=self.user,
            user_name=self.user.fullname,
            user_email=self.user.email,
            age="35",
            assessment_score=85,
            interpretation="Mild Dementia",
            assessment_date=datetime.now().date()
        )

    def test_client_creation(self):
        """Test that a FirstPersonClientDetails instance is created successfully."""
        self.assertEqual(FirstPersonClientDetails.objects.count(), 1)
        self.assertEqual(self.client_details.fullname, "Jane Doe")
        self.assertEqual(self.client_details.user, self.user)
        self.assertEqual(self.client_details.age, "35")
        self.assertEqual(self.client_details.assessment_score, 85)
        self.assertEqual(self.client_details.interpretation, "Mild Dementia")

    def test_null_fields(self):
        """Test that null and blank fields are allowed."""
        client = FirstPersonClientDetails.objects.create()
        self.assertIsNone(client.fullname)
        self.assertIsNone(client.user)
        self.assertIsNone(client.user_name)
        self.assertIsNone(client.user_email)
        self.assertIsNone(client.age)
        self.assertIsNone(client.assessment_score)
        self.assertIsNone(client.interpretation)


    def test_default_assessment_date(self):
        """Test that the default value for assessment_date is set correctly."""
        client = FirstPersonClientDetails.objects.create()
        # Compare only the date part of the assessment_date field
        self.assertEqual(client.assessment_date.date(), datetime.now().date())


    def test_str_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.client_details), "Jane Doe")





class NewsLetterSubscriptionModelTest(TestCase):
    
    def setUp(self):
        """Create a test newsletter subscription."""
        self.subscription = NewsLetterSubscription.objects.create(
            email="testuser@example.com"
        )
    
    def test_subscription_creation(self):
        """Test that a subscription is created correctly."""
        self.assertEqual(NewsLetterSubscription.objects.count(), 1)
        self.assertEqual(self.subscription.email, "testuser@example.com")
        self.assertEqual(self.subscription.subscribed_on, date.today())
    
    def test_email_unique_constraint(self):
        """Test that an email address cannot be duplicated."""
        with self.assertRaises(Exception):  # This will raise an IntegrityError
            NewsLetterSubscription.objects.create(
                email="testuser@example.com"
            )
    
    def test_str_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.subscription), "testuser@example.com")