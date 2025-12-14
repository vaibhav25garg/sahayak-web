# apps/categories/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer

from django.http import JsonResponse
from .models import Category

# def get_subcategories(request, parent_id):
#     subs = Category.objects.filter(parent_id=parent_id)
#     data = [{"id": s.id, "name": s.name} for s in subs]
#     return JsonResponse({"subcategories": data})

def get_subcategories(request, parent_id):
    subs = Category.objects.filter(parent_id=parent_id).values('id','name')
    data = list(subs)  # [{'id':..., 'name':...}, ...]
    return JsonResponse({"subcategories": data})

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type']
    search_fields = ['name', 'code']
    ordering_fields = ['priority', 'name']
    ordering = ['priority']
