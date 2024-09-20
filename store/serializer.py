from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection , Review, Cart, CartItem

class CollectionSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Collection  
        fields = ['id', 'title', 'products_count'] 
    products_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'slug', 'title', 'description', 'unit_price', 'inventory', 'price_with_tax', 'collection'] # we can keep other non-existing fields down the bottom like before.
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.09)   # .quantize(Decimal('0.01'))
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']
    
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return self.items * cart_item.product.unit_price
    class Meta:
        model = CartItem
        fields = ['uid', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    class Meta:
        model = Cart
        fields = ['uid', 'items', 'total_price']


