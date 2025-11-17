# apps/calling_summary/serializers.py
from rest_framework import serializers
from .models import CallingSummary

class CallingSummaryListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    
    class Meta:
        model = CallingSummary
        fields = [
            'id', 'caller_name', 'name', 'phone', 'location',
            'category', 'category_name', 'worker', 'worker_name',
            'status', 'payment_received', 'scheduled_at', 'created_at'
        ]

class CallingSummaryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallingSummary
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

