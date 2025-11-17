# apps/ivr/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import IVR
from .serializers import IVRSerializer

class IVRViewSet(viewsets.ModelViewSet):
    """
    ViewSet for IVR CRUD operations
    """
    queryset = IVR.objects.all().select_related('called_worker')
    serializer_class = IVRSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['response', 'campaign_id', 'called_worker']
    search_fields = ['number', 'name', 'auto_campaign_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

