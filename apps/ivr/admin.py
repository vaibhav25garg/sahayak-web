# apps/ivr/admin.py
from django.contrib import admin
from .models import IVR

@admin.register(IVR)
class IVRAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'number', 'name', 'called_worker',
        'response', 'auto_campaign_name', 'created_at'
    ]
    list_filter = ['response', 'auto_campaign_name', 'created_at']
    search_fields = ['number', 'name', 'campaign_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
