# apps/locations/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location
from .serializers import LocationSerializer

class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Location CRUD operations
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pincode', 'city', 'state']
    search_fields = ['area_code', 'pincode', 'city', 'street_address']
    ordering_fields = ['city', 'pincode']
    ordering = ['city']
