from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from admin_side.models import Service, DoctorProfile
from user_side.models import Appointment

# 1️⃣ Static Pages Sitemap (Frontend React Routes)
class StaticViewSitemap(Sitemap):
    priority = 0.5  # Default importance
    changefreq = "weekly"

    def items(self):
        return [
            'home', 'signup', 'otp-verification', 'login', 'about', 'services',
            'contact', 'doctor-consulting', 'booking-confirmation', 'success',
            'create-meet', 'user-profile', 'appointments-history', 'assessment-history',
            'assessment', 'self-assessment', 'self-assessment-instructions',
            'first-person-assessment', 'first-person-assessment-instructions',
            'first-person-assessment-client-details', 'first-person-assessment-user-details',
            'first-person-assessment-results', 'first-person-assessment-new-user',
            'terms-conditions', 'privacy-policy', 'careers'
        ]

    def location(self, item):
        return reverse(item)  # Converts names to URLs

# 2️⃣ Services Sitemap (Dynamic)
class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Service.objects.all()

    def location(self, obj):
        return f"/services/{obj.id}/"  # Assuming React uses service ID

# 3️⃣ Doctors Sitemap (Dynamic)
class DoctorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return DoctorProfile.objects.all()

    def location(self, obj):
        return f"/doctor-consulting/doctor-details/{obj.id}/"

# 4️⃣ Appointments Sitemap (Optional for user history pages)
class AppointmentSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Appointment.objects.all()

    def location(self, obj):
        return f"/user-profile/appointments-history/{obj.id}/"

# Register all sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'doctors': DoctorSitemap,
    'appointments': AppointmentSitemap,
}
