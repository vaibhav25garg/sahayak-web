from django.contrib import admin

# Register your models here.
# apps/requirements/admin.py
from django.contrib import admin
from .models import Requirement

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'requirement_id', 'name', 'number',
        'category', 'worker', 'status', 'scheduled_date'
    ]
    list_filter = ['status', 'category', 'scheduled_date', 'created_at']
    search_fields = ['requirement_id', 'name', 'number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'