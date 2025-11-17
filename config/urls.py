# ============================================================
# config/urls.py - Update
# ============================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Customize admin site
admin.site.site_header = "ServiceConnect Admin Panel"
admin.site.site_title = "ServiceConnect Admin"
admin.site.index_title = "Welcome to Management Panel"

# Import viewsets
from apps.workers.views import WorkerViewSet
from apps.tasks.views import TaskViewSet
from apps.categories.views import CategoryViewSet
from apps.locations.views import LocationViewSet
from apps.calling_summary.views import CallingSummaryViewSet
from apps.ivr.views import IVRViewSet
from apps.requirements.views import RequirementViewSet

# Create API router
router = DefaultRouter()
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'calling-summary', CallingSummaryViewSet, basename='calling-summary')
router.register(r'ivr', IVRViewSet, basename='ivr')
router.register(r'requirements', RequirementViewSet, basename='requirement')

urlpatterns = [
    # Hidden Django Admin (for superuser only)
    path(settings.ADMIN_URL, admin.site.urls),
    
    # Custom Dashboard (authenticated admin interface)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Public URLs (No authentication required)
    path('', include('apps.public.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)