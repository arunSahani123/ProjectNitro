from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

# API Documentation
schema_view = get_schema_view(
   openapi.Info(
      title="File Parser CRUD API",
      default_version='v1',
      description="API for uploading, parsing, and managing files with progress tracking",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@fileparser.local"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Simple health check view
def health_check(request):
    return JsonResponse({"status": "ok"})

# Homepage view
def home(request):
    return JsonResponse({"message": "File upload or processing in progress. Please try again later"})

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/files/', include('files.urls')),

    # Health check
    path('api/health/', health_check),

    # Root URL
    path('', home),
]

# Serve media & static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
