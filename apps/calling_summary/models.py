from django.db import models
from apps.tasks.models import Task
from apps.workers.models import Worker
from apps.categories.models import Category
import string, random


def generate_random_id(length=None):
    if length is None:
        length = random.randint(15, 20)
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


class CallingSummary(models.Model):

    ACTION_CHOICES = (
        ("created", "Created"),
        ("updated", "Updated"),
        ("status_changed", "Status Changed"),
        ("worker_assigned", "Worker Assigned"),
    )

    id = models.CharField(primary_key=True, max_length=25, editable=False)

    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="call_logs"
    )

    # Customer
    caller_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    location = models.TextField()

    # Service
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name="call_categories"
    )
    subcategory = models.CharField(max_length=200, blank=True, null=True)

    # Worker
    worker = models.ForeignKey(
        Worker, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="call_assignments"
    )
    worker_assigned = models.CharField(max_length=200, blank=True, null=True)

    # Action tracking
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    status = models.CharField(max_length=50)
    changes = models.JSONField(blank=True, null=True)

    # Payment
    payment_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Time
    scheduled_at = models.DateTimeField()
    submit_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calling_summary"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_random_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Log {self.action} | Task {self.task_id}"
