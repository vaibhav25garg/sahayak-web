# apps/tasks/serializers.py
from rest_framework import serializers
from .models import Task
from apps.categories.serializers import CategorySerializer
from apps.workers.serializers import WorkerListSerializer

class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task list"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    worker_phone = serializers.CharField(source='worker.phone', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'cust_name', 'cust_phone', 'cust_location',
            'category', 'category_name', 'worker', 'worker_name',
            'worker_phone', 'schedule_date', 'status',
            'payment_received_amt', 'rating', 'created_at'
        ]

class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single task view"""
    category_detail = CategorySerializer(source='category', read_only=True)
    subcategories_detail = CategorySerializer(source='subcategories', many=True, read_only=True)
    worker_detail = WorkerListSerializer(source='worker', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks"""
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_cust_phone(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value
    
    def validate_rating(self, value):
        if value and (value < 0 or value > 5):
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return value