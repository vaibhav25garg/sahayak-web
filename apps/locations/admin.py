# apps/locations/admin.py
from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'area_code', 'pincode', 'city',
        'state', 'created_at'
    ]
    list_filter = ['state', 'city', 'created_at']
    search_fields = ['area_code', 'pincode', 'city', 'street_address']
    readonly_fields = ['created_at', 'updated_at']