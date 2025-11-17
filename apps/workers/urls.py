# apps/workers/urls.py (for template views)
from django.urls import path
from . import template_views

app_name = 'workers'

urlpatterns = [
    path('', template_views.home, name='home'),
    path('workers/', template_views.worker_list, name='worker_list'),
    path('workers/create/', template_views.worker_create, name='worker_create'),
    path('workers/<int:pk>/', template_views.worker_detail, name='worker_detail'),
    path('workers/<int:pk>/edit/', template_views.worker_edit, name='worker_edit'),
    path('workers/<int:pk>/delete/', template_views.worker_delete, name='worker_delete'),
]

