# apps/calling_summary/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CallingSummary
from .serializers import CallingSummaryListSerializer, CallingSummaryDetailSerializer

class CallingSummaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Calling Summary CRUD operations
    """
    queryset = CallingSummary.objects.all().select_related('task', 'worker', 'category')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'worker', 'scheduled_at']
    search_fields = ['caller_name', 'name', 'phone']
    ordering_fields = ['scheduled_at', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CallingSummaryListSerializer
        return CallingSummaryDetailSerializer

