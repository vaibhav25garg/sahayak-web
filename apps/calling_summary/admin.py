# apps/calling_summary/admin.py
from django.contrib import admin
from .models import CallingSummary

@admin.register(CallingSummary)
class CallingSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'caller_name', 'name', 'phone',
        'category', 'worker', 'status', 'scheduled_at'
    ]
    list_filter = ['status', 'category', 'scheduled_at', 'created_at']
    search_fields = ['caller_name', 'name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_at'
