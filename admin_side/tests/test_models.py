from django.test import TestCase
from admin_side.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from datetime import date, time



class ServiceModelTest(TestCase):

    def setUp(self):
        """Set up test data."""
        # Create a dummy SVG file
        self.valid_svg = SimpleUploadedFile(
            "test_image.svg",
            b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>',
            content_type="image/svg+xml"
        )
        self.service = Service.objects.create(
            title="Test Service",
            description="This is a test service description.",
            image=self.valid_svg
        )

    def test_service_creation(self):
        """Test that a Service instance is created correctly."""
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(self.service.title, "Test Service")
        self.assertEqual(self.service.description, "This is a test service description.")
        self.assertTrue(self.service.image.name.endswith(".svg"))  # Updated check

    def test_str_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.service), "Test Service")

    def test_invalid_image_file(self):
        """Test that invalid files are rejected by the image field validator."""
        invalid_file = SimpleUploadedFile(
            "test_image.txt",
            b"This is not an SVG file.",
            content_type="text/plain"
        )
        with self.assertRaises(ValidationError):  # Updated to ValidationError
            service = Service(
                title="Invalid Service",
                description="Invalid file upload test",
                image=invalid_file
            )
            service.full_clean()





class DoctorProfileModelTest(TestCase):

    def setUp(self):
        """Set up test data."""
        self.profile_picture = SimpleUploadedFile(
            "profile_picture.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            specialization="Cardiology",
            schedule="Mon-Fri 9AM-5PM",
            details="Experienced cardiologist with over 10 years of practice.",
            consulting_fee=500.00,
            profile_picture=self.profile_picture,
            category="doctor"
        )

    def test_doctor_profile_creation(self):
        """Test that a DoctorProfile instance is created correctly."""
        self.assertEqual(DoctorProfile.objects.count(), 1)
        self.assertEqual(self.doctor.doctor_name, "Dr. John Doe")
        self.assertEqual(self.doctor.email, "johndoe@example.com")
        self.assertEqual(self.doctor.mobile, "1234567890")
        self.assertEqual(self.doctor.specialization, "Cardiology")
        self.assertEqual(self.doctor.schedule, "Mon-Fri 9AM-5PM")
        self.assertEqual(self.doctor.details, "Experienced cardiologist with over 10 years of practice.")
        self.assertEqual(self.doctor.consulting_fee, 500.00)
        self.assertEqual(self.doctor.category, "doctor")
        self.assertIn("profile_picture", self.doctor.profile_picture.name)

        # Validate that the file is stored in the correct directory
        self.assertTrue(self.doctor.profile_picture.name.startswith("doctor_profile_picture/"))

    def test_null_fields(self):
        """Test that default values work correctly for null/blank fields."""
        doctor = DoctorProfile.objects.create(
            doctor_name="Dr. Jane Doe",
            specialization="Pediatrics",
            schedule="Tue-Thu 10AM-4PM",
            details="Specialist in child healthcare.",
            consulting_fee=300.00,
            profile_picture=self.profile_picture,
            category="geriatric_counselor"
        )
        self.assertEqual(doctor.email, "example@example.com")
        self.assertEqual(doctor.mobile, "0000000000")

    def test_string_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.doctor), "Dr. John Doe")





class TimeSlotModelTest(TestCase):

    def setUp(self):
        """Set up a doctor and a timeslot instance for testing."""
        image = SimpleUploadedFile(
            "profile_picture.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        # Create a doctor profile
        self.doctor = DoctorProfile.objects.create(
            doctor_name="Dr. John Doe",
            email="doctor@example.com",
            mobile="1234567890",
            specialization="Geriatrics",
            schedule="9:00 AM - 5:00 PM",
            details="Experienced in treating dementia patients.",
            consulting_fee=100.00,
            profile_picture=image
        )

        # Create a TimeSlot instance
        self.timeslot = TimeSlot.objects.create(
            day="Monday",
            start_time=time(9, 0),  # 9:00 AM
            end_time=time(10, 0),    # 10:00 AM
            doctor=self.doctor,
            is_booked=False
        )

    def test_doctor_profile_creation(self):
        """Test that a DoctorProfile instance is created correctly."""
        self.assertEqual(DoctorProfile.objects.count(), 1)
        self.assertEqual(self.doctor.doctor_name, "Dr. John Doe")

        # Check if the profile_picture path contains the expected base file name
        self.assertIn("profile_picture", self.doctor.profile_picture.name)

        # Optional: Check if the path starts with the expected directory
        self.assertTrue(self.doctor.profile_picture.name.startswith("doctor_profile_picture/"))



    def test_timeslot_creation(self):
        """Test that a TimeSlot instance is created correctly."""
        self.assertEqual(TimeSlot.objects.count(), 1)
        self.assertEqual(self.timeslot.day, "Monday")
        self.assertEqual(self.timeslot.start_time, time(9, 0))
        self.assertEqual(self.timeslot.end_time, time(10, 0))
        self.assertEqual(self.timeslot.doctor, self.doctor)
        self.assertFalse(self.timeslot.is_booked)

    def test_invalid_day_choice(self):
        """Test that invalid day raises a validation error."""
        invalid_timeslot = TimeSlot(
            day="InvalidDay",  # Invalid day
            start_time=time(9, 0),
            end_time=time(10, 0),
            doctor=self.doctor,
            is_booked=False
        )
        with self.assertRaises(ValidationError):
            invalid_timeslot.full_clean()

    def test_timeslot_string_representation(self):
        """Test the string representation of the TimeSlot model."""
        self.assertEqual(str(self.timeslot), "Dr. John Doe - Monday 09:00:00 to 10:00:00")

    def test_time_overlap(self):
        """Test that two time slots with overlapping times are not allowed (for the same doctor)."""
        # Create another TimeSlot with overlapping times
        overlapping_timeslot = TimeSlot(
            day="Monday",
            start_time=time(9, 30),  # Overlaps with the existing timeslot
            end_time=time(10, 30),
            doctor=self.doctor,
            is_booked=False
        )
        with self.assertRaises(ValidationError):
            overlapping_timeslot.full_clean()

    def test_timeslot_booking_status(self):
        """Test that the `is_booked` field updates correctly."""
        self.timeslot.is_booked = True
        self.timeslot.save()

        # Verify that the is_booked field is updated
        self.assertTrue(self.timeslot.is_booked)



    def test_valid_day_choices(self):
        """Test that the `day` field accepts only valid choices."""
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Clear existing time slots for the doctor to avoid overlaps
        TimeSlot.objects.filter(doctor=self.doctor).delete()

        for index, day in enumerate(valid_days):
            # Ensure each time slot is unique
            start_time = time(9 + index, 0)
            end_time = time(10 + index, 0)

            timeslot = TimeSlot(
                day=day,
                start_time=start_time,
                end_time=end_time,
                doctor=self.doctor,
                is_booked=False
            )
            try:
                timeslot.full_clean()  # Should not raise any error for valid days
            except ValidationError as e:
                self.fail(f"{day} should be a valid choice for the day field, but error occurred: {e}")
