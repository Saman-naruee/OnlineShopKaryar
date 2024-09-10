from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection

class CollectionSerializer(serializers.ModelSerializer):  
    products = serializers.SerializerMethodField()  # Method field for products  

    class Meta:  
        model = Collection  
        fields = ['id', 'title', 'products'] 

    def get_products(self, collection):  
        data = ProductSerializer(collection.product_set.all(), many=True).data  
        return len(data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'slug', 'title', 'description', 'unit_price', 'inventory', 'price_with_tax', 'collection'] # we can keep other non-existing fields down the bottom like before.
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.09)   # .quantize(Decimal('0.01'))
    
