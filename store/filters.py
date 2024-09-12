from django_filters import FilterSet
from .models import Product
"""
for more information:
    https://django-filter.readthedocs.io/en/stable/
learn : generic filters.
"""
class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }