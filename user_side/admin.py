from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Enquiries)
admin.site.register(Appointment)
admin.site.register(Order)
admin.site.register(FirstPersonClientDetails)
admin.site.register(NewsLetterSubscription)
admin.site.register(SelfAssessment)