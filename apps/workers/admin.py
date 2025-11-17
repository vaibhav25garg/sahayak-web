
# apps/workers/admin.py
from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'phone', 'primary_category',
        'verification_status', 'ranking_score', 'created_at'
    ]
    list_filter = [
        'verification_status', 'primary_category',
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'phone', 'aadhar_no']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['secondary_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone', 'whatsapp_no', 'age', 'aadhar_no')
        }),
        ('Category & Location', {
            'fields': ('primary_category', 'secondary_categories', 'location', 'geo_location_link')
        }),
        ('Work Information', {
            'fields': ('last_working_at', 'task_id_lst', 'busy_dates', 'ranking_score')
        }),
        ('Verification', {
            'fields': (
                'verification_status', 'aadhar_img_front',
                'aadhar_img_back', 'selfie_img'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_workers', 'reject_workers']
    
    def verify_workers(self, request, queryset):
        updated = queryset.update(verification_status='verified')
        self.message_user(request, f'{updated} workers verified successfully.')
    verify_workers.short_description = "Verify selected workers"
    
    def reject_workers(self, request, queryset):
        updated = queryset.update(verification_status='rejected')
        self.message_user(request, f'{updated} workers rejected.')
    reject_workers.short_description = "Reject selected workers"