from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection

class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length = 255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = serializers.HyperlinkedRelatedField( # all way to serialize a relation: 1.primary key 2.string 3.Nested object 4.Hyperlinks
        queryset = Collection.objects.all(),
        view_name = 'collection-detail'
    )

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.09)   # .quantize(Decimal('0.01'))