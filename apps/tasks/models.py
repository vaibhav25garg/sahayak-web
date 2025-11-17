# apps/tasks/models.py
from django.db import models
from apps.categories.models import Category
from apps.workers.models import Worker

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Customer Information
    cust_name = models.CharField(max_length=200)
    cust_phone = models.CharField(max_length=15)
    cust_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    cust_location = models.TextField()
    pincode = models.CharField(max_length=10)
    
    # Task Details
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
    
    # Worker Assignment
    worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    worker_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Scheduling
    schedule_date = models.DateTimeField()
    day_service_done = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment and Feedback
    payment_received_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    feedback = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Task #{self.id} - {self.cust_name} ({self.status})"
