# apps/tasks/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from .models import Task
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateUpdateSerializer
)

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations
    """
    queryset = Task.objects.all().select_related('category', 'worker')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'worker', 'schedule_date']
    search_fields = ['cust_name', 'cust_phone', 'pincode']
    ordering_fields = ['schedule_date', 'created_at', 'payment_received_amt']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer
    
    @action(detail=True, methods=['post'])
    def assign_worker(self, request, pk=None):
        """Assign a worker to the task"""
        task = self.get_object()
        worker_id = request.data.get('worker_id')
        
        if not worker_id:
            return Response(
                {'error': 'worker_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.workers.models import Worker
        try:
            worker = Worker.objects.get(id=worker_id)
            task.worker = worker
            task.worker_name = worker.name
            task.status = 'scheduled'
            task.save()
            
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response(
                {'error': 'Worker not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.day_service_done = request.data.get('completion_date')
        task.payment_received_amt = request.data.get('payment_amount', task.payment_received_amt)
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        """Add feedback and rating to task"""
        task = self.get_object()
        task.feedback = request.data.get('feedback')
        task.rating = request.data.get('rating')
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics"""
        stats = {
            'total': self.queryset.count(),
            'pending': self.queryset.filter(status='pending').count(),
            'scheduled': self.queryset.filter(status='scheduled').count(),
            'active': self.queryset.filter(status='active').count(),
            'completed': self.queryset.filter(status='completed').count(),
            'average_rating': self.queryset.filter(rating__isnull=False).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating']
        }
        return Response(stats)
