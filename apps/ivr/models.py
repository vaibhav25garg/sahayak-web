# apps/ivr/models.py
from django.db import models
from apps.workers.models import Worker

class IVR(models.Model):
    RESPONSE_CHOICES = (
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
    )
    
    number = models.CharField(max_length=15)
    name = models.CharField(max_length=200, blank=True, null=True)
    
    # Worker Called
    called_worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ivr_calls'
    )
    
    # Response Details
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES)
    code = models.CharField(max_length=50, blank=True, null=True)
    total_response_time = models.DurationField(blank=True, null=True)
    
    # Campaign Details
    auto_campaign_name = models.CharField(max_length=200, blank=True, null=True)
    campaign_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ivr'
        verbose_name = 'IVR Log'
        verbose_name_plural = 'IVR Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"IVR #{self.id} - {self.number} ({self.response})"
