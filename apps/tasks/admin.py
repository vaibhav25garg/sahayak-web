# apps/tasks/admin.py
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cust_name', 'cust_phone', 'category',
        'worker', 'status', 'schedule_date', 'payment_received_amt',
        'location'   # NEW
    ]

    list_filter = [
        'status', 'category', 'schedule_date',
        'created_at', 'location'  # NEW
    ]

    search_fields = ['cust_name', 'cust_phone', 'pincode']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['subcategories']
    date_hierarchy = 'schedule_date'

    fieldsets = (
        ('Customer Information', {
            'fields': (
                'cust_name', 'cust_phone', 'cust_whatsapp',
                'cust_location', 'pincode', 'location'  # NEW
            )
        }),
        ('Task Details', {
            'fields': (
                'category', 'subcategories', 'additional_info',
                'task_image'
            )
        }),
        ('Worker Assignment', {
            'fields': ('worker', 'worker_name')
        }),
        ('Scheduling & Status', {
            'fields': (
                'schedule_date', 'day_service_done', 'status'
            )
        }),
        ('Payment & Feedback', {
            'fields': (
                'payment_received_amt', 'feedback', 'rating'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_completed', 'mark_as_active']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} tasks marked as active.')
    mark_as_active.short_description = "Mark as active"
