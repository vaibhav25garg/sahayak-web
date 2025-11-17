# apps/workers/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Worker
from .serializers import (
    WorkerListSerializer, 
    WorkerDetailSerializer, 
    WorkerCreateUpdateSerializer
)

class WorkerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Worker CRUD operations
    """
    queryset = Worker.objects.all().select_related('primary_category', 'location')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verification_status', 'primary_category', 'location']
    search_fields = ['name', 'phone', 'aadhar_no']
    ordering_fields = ['ranking_score', 'created_at', 'name']
    ordering = ['-ranking_score']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkerCreateUpdateSerializer
        return WorkerDetailSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Custom action to verify a worker"""
        worker = self.get_object()
        worker.verification_status = 'verified'
        worker.save()
        serializer = self.get_serializer(worker)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Custom action to reject a worker"""
        worker = self.get_object()
        worker.verification_status = 'rejected'
        worker.save()
        serializer = self.get_serializer(worker)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available workers (verified and not busy)"""
        date = request.query_params.get('date')
        category = request.query_params.get('category')
        
        workers = self.queryset.filter(verification_status='verified')
        
        if category:
            workers = workers.filter(primary_category_id=category)
        
        serializer = self.get_serializer(workers, many=True)
        return Response(serializer.data)

