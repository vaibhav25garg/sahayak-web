# apps/categories/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'category_type', 'priority', 'created_at']
    list_filter = ['category_type', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['priority', 'name']
