from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from user_side.sitemaps import sitemaps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_side.urls')),
    path('admin-side/', include('admin_side.urls')),
    path('api-auth', include('rest_framework.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)