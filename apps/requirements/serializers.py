# apps/requirements/serializers.py
from rest_framework import serializers
from .models import Requirement

class RequirementListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    
    class Meta:
        model = Requirement
        fields = [
            'id', 'requirement_id', 'name', 'number', 'location',
            'category', 'category_name', 'worker', 'worker_name',
            'status', 'scheduled_date', 'created_at'
        ]

class RequirementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')