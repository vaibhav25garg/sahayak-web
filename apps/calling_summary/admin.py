from django.contrib import admin
from .models import CallingSummary


@admin.register(CallingSummary)
class CallingSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "action",
        "status",
        "caller_name",
        "phone",
        "category",
        "worker",
        "scheduled_at",
        "created_at",
    )

    list_filter = (
        "action",
        "status",
        "category",
        "scheduled_at",
        "created_at",
    )

    search_fields = (
        "caller_name",
        "name",
        "phone",
        "task__id",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "submit_time",
    )

    date_hierarchy = "created_at"
