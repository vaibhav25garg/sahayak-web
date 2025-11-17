# apps/locations/models.py
import string
import random
from django.db import models


def generate_random_id(length=None):
    """Generate random alphanumeric ID (15–20 chars)."""
    if length is None:
        length = random.randint(15, 20)
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class Location(models.Model):
    # Primary Key with random string ID
    id = models.CharField(
        primary_key=True,
        max_length=25,
        editable=False,
        unique=True
    )

    area_code = models.CharField(max_length=50, unique=True, db_index=True)
    pincode = models.CharField(max_length=10)
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    geo_latitude = models.FloatField(blank=True, null=True)
    geo_longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations'
        ordering = ['city', 'area_code']

    def save(self, *args, **kwargs):
        """Generate unique random ID only once when created."""
        if not self.id:
            new_id = generate_random_id()

            while Location.objects.filter(id=new_id).exists():
                new_id = generate_random_id()

            self.id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.area_code} - {self.city}, {self.state}"
