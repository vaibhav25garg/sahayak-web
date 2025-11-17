# apps/categories/serializers.py
from rest_framework import serializers
from .models import Category


class SubCategorySerializer(serializers.ModelSerializer):
    """Used to show subcategories inside a parent category"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'code', 'priority')


class CategorySerializer(serializers.ModelSerializer):
    # Show subcategories only for primary categories
    subcategories = SubCategorySerializer(many=True, read_only=True)

    # Show parent name for subcategories
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'code',
            'category_type',
            'priority',
            'parent',
            'parent_name',
            'subcategories',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """
        Enforce relationship rules:
        - Only subcategories can have a parent.
        - Subcategories must have a primary parent.
        - Primary categories cannot have a parent.
        """
        category_type = data.get('category_type', getattr(self.instance, 'category_type', None))
        parent = data.get('parent', getattr(self.instance, 'parent', None))

        if category_type == 'primary' and parent:
            raise serializers.ValidationError("Primary categories cannot have a parent.")
        if category_type == 'subcategory' and parent and parent.category_type != 'primary':
            raise serializers.ValidationError("Subcategory must belong to a primary category.")
        if category_type == 'subcategory' and not parent:
            raise serializers.ValidationError("Subcategory must have a parent category.")
        return data
