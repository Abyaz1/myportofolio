# Main URL routing configuration for myportofolio project.
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin and main web application routes.
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    # REST API and browsable API authentication routes.
    path('api/v1/', include('main.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
]
