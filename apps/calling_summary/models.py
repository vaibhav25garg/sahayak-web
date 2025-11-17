# apps/calling_summary/models.py
from django.db import models
from apps.tasks.models import Task
from apps.workers.models import Worker
from apps.categories.models import Category
import string
import random


def generate_random_id(length=None):
    """Generate random alphanumeric ID (15–20 chars)."""
    if length is None:
        length = random.randint(15, 20)
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class CallingSummary(models.Model):

    # Primary Key: random string
    id = models.CharField(
        primary_key=True,
        max_length=25,
        editable=False,
        unique=True
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_logs'
    )
    
    # Caller Details
    caller_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    location = models.TextField()
    
    # Service Details
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='call_categories'
    )
    subcategory = models.CharField(max_length=200, blank=True, null=True)
    
    # Worker Assignment
    worker_assigned = models.CharField(max_length=200, blank=True, null=True)
    worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_assignments'
    )
    
    # Status and Payment
    status = models.CharField(max_length=50)
    payment_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Feedback
    feedback = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Timestamps
    scheduled_at = models.DateTimeField()
    submit_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calling_summary'
        verbose_name_plural = 'Calling Summaries'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Generate unique random ID only on creation."""
        if not self.id:
            new_id = generate_random_id()
            while CallingSummary.objects.filter(id=new_id).exists():
                new_id = generate_random_id()
            self.id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Call Log #{self.id} - {self.name}"
