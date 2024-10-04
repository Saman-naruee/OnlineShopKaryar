from django_filters import FilterSet
from .models import Product, Collection
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


class CollectionFilter(FilterSet):
    class Meta:
        model = Collection
        fields = {
            'title': ['exact'],
            'featured_product': ['exact']
        }