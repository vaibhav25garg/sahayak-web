# apps/workers/serializers.py
from rest_framework import serializers
from .models import Worker
from apps.categories.serializers import CategorySerializer
from apps.locations.serializers import LocationSerializer

class WorkerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    primary_category_name = serializers.CharField(source='primary_category.name', read_only=True)
    location_name = serializers.CharField(source='location.area_code', read_only=True)
    
    class Meta:
        model = Worker
        fields = [
            'id', 'name', 'phone', 'whatsapp_no', 'age',
            'primary_category', 'primary_category_name',
            'location', 'location_name', 'ranking_score',
            'verification_status', 'created_at'
        ]

class WorkerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single worker view"""
    primary_category_detail = CategorySerializer(source='primary_category', read_only=True)
    secondary_categories_detail = CategorySerializer(source='secondary_categories', many=True, read_only=True)
    location_detail = LocationSerializer(source='location', read_only=True)
    
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class WorkerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workers"""
    
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_phone(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value
    
    def validate_aadhar_no(self, value):
        if value and (not value.isdigit() or len(value) != 12):
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits")
        return value
