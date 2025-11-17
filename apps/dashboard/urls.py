# ============================================================
# apps/dashboard/urls.py
# ============================================================
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard Home
    path('', views.dashboard_home, name='home'),
    
    # Worker Management (Bucket 1)
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<str:pk>/', views.worker_detail, name='worker_detail'),
    path('workers/<str:pk>/verify/', views.worker_verify, name='worker_verify'),
    path('workers/<str:pk>/reject/', views.worker_reject, name='worker_reject'),
    
    # Task Management (Bucket 2)
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<str:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<str:pk>/assign/', views.task_assign_worker, name='task_assign_worker'),
    path('tasks/<str:pk>/update-status/', views.task_update_status, name='task_update_status'),
    path('tasks/create-from-requirement/<str:requirement_id>/', 
         views.task_create_from_requirement, name='task_create_from_requirement'),
    
    # Task Log History (Bucket 3)
    path('logs/', views.task_log_history, name='task_log_history'),
    path('requirements/<str:pk>/', views.requirement_detail, name='requirement_detail'),

    # Worker PDF / CRUD
    path('workers/pdf/<str:pk>/', views.worker_pdf, name='worker_pdf'),
    path('workers/add/', views.worker_add, name='worker_add'),
    path('workers/update/<str:pk>/', views.worker_edit, name='worker_edit'),
    path('workers/delete/<str:pk>/', views.worker_delete, name='worker_delete'),
]
