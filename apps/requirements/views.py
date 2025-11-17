from django.shortcuts import render

# Create your views here.
# apps/requirements/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Requirement
from .serializers import RequirementListSerializer, RequirementDetailSerializer

class RequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Requirement CRUD operations
    """
    queryset = Requirement.objects.all().select_related('category', 'worker')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'worker']
    search_fields = ['requirement_id', 'name', 'number']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RequirementListSerializer
        return RequirementDetailSerializer