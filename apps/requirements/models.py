from django.db import models
import string, random

def generate_random_id(length=None):
    if length is None:
        length = random.randint(15, 20)
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class Requirement(models.Model):

    id = models.CharField(
        primary_key=True,
        max_length=25,
        editable=False,
        unique=True
    )

    requirement_id = models.CharField(max_length=100, unique=True)

    name = models.CharField(max_length=200)
    number = models.CharField(max_length=15)
    location = models.TextField()

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='requirements'
    )

    worker = models.ForeignKey(
        'workers.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requirements'
    )

    status = models.CharField(max_length=20, default='pending')
    scheduled_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            new_id = generate_random_id()
            while Requirement.objects.filter(id=new_id).exists():
                new_id = generate_random_id()
            self.id = new_id

        super().save(*args, **kwargs)
