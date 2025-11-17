
# ============================================================
# apps/public/urls.py - Same as before
# ============================================================
from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('join-as-worker/', views.worker_registration, name='worker_registration'),
    path('request-service/', views.requirement_form, name='requirement_form'),
]
