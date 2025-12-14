from django.forms.models import model_to_dict
from django.utils import timezone
from apps.calling_summary.models import CallingSummary


def get_changes(old, new, fields):
    changes = {}
    for f in fields:
        if old.get(f) != new.get(f):
            changes[f] = {
                "from": old.get(f),
                "to": new.get(f)
            }
    return changes

from django.utils import timezone
from datetime import datetime

def make_aware_datetime(dt_str):
    """
    Converts 'YYYY-MM-DDTHH:MM' to timezone-aware datetime
    """
    if not dt_str:
        return None

    naive = datetime.fromisoformat(dt_str)
    return timezone.make_aware(naive)

from decimal import Decimal
from django.utils import timezone

def make_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value

def log_task_change(task, action, old_task=None, performed_by="System"):
    changes = {}

    if old_task:
        fields = [
            "cust_name",
            "cust_phone",
            "cust_whatsapp",
            "pincode",
            "status",
            "schedule_date",
            "payment_received_amt",
            "worker_id",
        ]

        for field in fields:
            old_val = getattr(old_task, field)
            new_val = getattr(task, field)

            if old_val != new_val:
                changes[field] = {
                    "old": make_json_safe(old_val),
                    "new": make_json_safe(new_val),
                }

    CallingSummary.objects.create(
        task=task,
        caller_name=performed_by,
        name=task.cust_name,
        phone=task.cust_phone,
        location=task.cust_location,
        category=task.category,
        subcategory=", ".join(task.subcategories.values_list("name", flat=True)),
        worker=task.worker,
        worker_assigned=task.worker_name,
        action=action,
        status=task.status,
        payment_received=float(task.payment_received_amt or 0),
        changes=changes or None,
        scheduled_at=task.schedule_date or timezone.now(),
        submit_time=timezone.now(),
    )
