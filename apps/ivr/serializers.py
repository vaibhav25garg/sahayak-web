# apps/ivr/serializers.py
from rest_framework import serializers
from .models import IVR

class IVRSerializer(serializers.ModelSerializer):
    called_worker_name = serializers.CharField(source='called_worker.name', read_only=True)
    
    class Meta:
        model = IVR
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

