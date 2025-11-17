# apps/workers/models.py
import uuid
import string
import random
from django.db import models
from apps.categories.models import Category
from apps.locations.models import Location


def generate_random_id(length=None):
    """Generate random alphanumeric ID (15–20 chars)."""
    if length is None:
        length = random.randint(15, 20)  # dynamically choose length

    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class Worker(models.Model):
    # Custom Primary Key
    id = models.CharField(
        primary_key=True,
        max_length=25,     # safe for 20-char IDs
        editable=False,
        unique=True
    )

    VERIFICATION_STATUS = (
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
        ('pending', 'Pending'),
    )

    # Basic Information
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    whatsapp_no = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, unique=True, blank=True, null=True)

    # Category Information
    primary_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_workers'
    )
    secondary_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='secondary_workers'
    )

    # Location Information
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    geo_location_link = models.URLField(blank=True, null=True)

    # Work Information
    last_working_at = models.DateTimeField(blank=True, null=True)
    task_id_lst = models.TextField(blank=True, null=True)
    busy_dates = models.TextField(blank=True, null=True)
    ranking_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    aadhar_img_front = models.ImageField(upload_to='workers/aadhar/', blank=True, null=True)
    aadhar_img_back = models.ImageField(upload_to='workers/aadhar/', blank=True, null=True)
    selfie_img = models.ImageField(upload_to='workers/selfies/', blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workers'
        ordering = ['-ranking_score', 'name']

    def save(self, *args, **kwargs):
        """Generate ID only once on creation."""
        if not self.id:
            new_id = generate_random_id()

            # ensure uniqueness
            while Worker.objects.filter(id=new_id).exists():
                new_id = generate_random_id()

            self.id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.phone}"
