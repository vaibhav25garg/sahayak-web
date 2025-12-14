# apps/tasks/models.py
import string
import random
from django.db import models

from apps.categories.models import Category
from apps.workers.models import Worker
from apps.locations.models import Location
from apps.requirements.models import Requirement   # ✅ Added import


def generate_random_id(length=None):
    """Generate random alphanumeric ID (15–20 chars)."""
    if length is None:
        length = random.randint(15, 20)

    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class Task(models.Model):
    # --------------------------
    # 🔑 Primary Key
    # --------------------------
    id = models.CharField(
        primary_key=True,
        max_length=25,
        editable=False,
        unique=True
    )

    # --------------------------
    # STATUS OPTIONS
    # --------------------------
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    # --------------------------
    # 👤 Customer Information
    # --------------------------
    cust_name = models.CharField(max_length=200)
    cust_phone = models.CharField(max_length=15)
    cust_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    cust_location = models.TextField()
    pincode = models.CharField(max_length=10)

    # Fuzzy matched location (FK)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    # --------------------------
    # 📦 Requirement Link (NEW)
    # --------------------------
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    # --------------------------
    # 📝 Task Details
    # --------------------------
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tasks'
    )
    subcategories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='task_subcategories'
    )
    additional_info = models.TextField(blank=True, null=True)
    task_image = models.ImageField(upload_to='tasks/', blank=True, null=True)

    # --------------------------
    # 👷 Worker Assignment
    # --------------------------
    worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    worker_name = models.CharField(max_length=200, blank=True, null=True)
    worker_phone = models.CharField(max_length=20, blank=True, null=True)
    worker_category = models.CharField(max_length=200, blank=True, null=True)

    # --------------------------
    # 📅 Scheduling
    # --------------------------
    schedule_date = models.DateTimeField(null=True, blank=True)
    day_service_done = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # --------------------------
    # 💰 Payment & ⭐ Feedback
    # --------------------------
    payment_received_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    feedback = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    # --------------------------
    # 🕒 Metadata
    # --------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------------
    # ⚙ Meta
    # --------------------------
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']

    # --------------------------
    # 🔄 Auto-generate primary key
    # --------------------------
    def save(self, *args, **kwargs):
        if not self.id:
            new_id = generate_random_id()

            # Ensure uniqueness
            while Task.objects.filter(id=new_id).exists():
                new_id = generate_random_id()

            self.id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Task #{self.id} - {self.cust_name} ({self.status})"
