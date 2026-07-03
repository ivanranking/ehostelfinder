from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hostels import views as hostel_views

urlpatterns = [
    path('', include('hostels.urls')),
    path('admin/', admin.site.urls),
    path('ai-assistant/', hostel_views.ai_assistant, name='ai_assistant'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)