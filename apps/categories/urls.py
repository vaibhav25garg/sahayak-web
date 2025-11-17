from django.urls import path
from .views import get_subcategories

urlpatterns = [
    path('get-subcategories/<str:parent_id>/', get_subcategories, name='get_subcategories'),
]