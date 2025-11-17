# apps/categories/models.py

import random
import string
from django.db import models

def generate_random_id(length=None):
    if length is None:
        length = random.randint(15, 20)
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class Category(models.Model):

    id = models.CharField(
        primary_key=True,
        max_length=25,
        editable=False,
        unique=True
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category_type = models.CharField(
        max_length=20,
        choices=(('primary', 'Primary Category'), ('subcategory', 'Subcategory')),
        default='primary'
    )
    priority = models.IntegerField(default=0)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        limit_choices_to={'category_type': 'primary'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['priority', 'name']

    def save(self, *args, **kwargs):
        if not self.id:
            new_id = generate_random_id()
            while Category.objects.filter(id=new_id).exists():
                new_id = generate_random_id()
            self.id = new_id
        super().save(*args, **kwargs)

    def __str__(self):
        if self.category_type == 'primary':
            return f"{self.name} ({self.code})"
        elif self.category_type == 'subcategory' and self.parent:
            return f"{self.parent.name} → {self.name} ({self.code})"
        return self.name
