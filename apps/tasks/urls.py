# apps/tasks/urls.py (for template views)
from django.urls import path
from . import template_views

app_name = 'tasks'

urlpatterns = [
    path('', template_views.task_list, name='task_list'),
    path('create/', template_views.task_create, name='task_create'),
    path('<int:pk>/', template_views.task_detail, name='task_detail'),
    path('<int:pk>/edit/', template_views.task_edit, name='task_edit'),
    path('<int:pk>/delete/', template_views.task_delete, name='task_delete'),
    path('<int:pk>/assign/', template_views.task_assign_worker, name='task_assign_worker'),
]