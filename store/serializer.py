from operator import truediv
from django.db import transaction
from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection , Review, Cart, CartItem, \
      Customer, Order, OrderItem, Notification, ProductImages
from core.models import User

class CollectionSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Collection  
        fields = ['id', 'title', 'products_count'] 
    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_pk']
        return ProductImages.objects.create(product_id=product_id, **validated_data)
    
    class Meta:
        model = ProductImages
        fields = ['pk', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'title', 'description', 'unit_price',
            'inventory', 'price_with_tax', 'collection', 'images'
            ] # we can keep other non-existing fields down the bottom like before.
        
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
        return cart_item.quantity * cart_item.product.unit_price
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

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField() 

    def validate_product_id(self, value): # validate method: validate_ + field (product_id)
        if  not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Does not found any product match with this id.')
        return value
    def save(self, **kwargs):
        cart_id = self.context['cart_id'] # came from view: overrided of get_serializer_context
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            # update an existing item
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # create a new item
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance
    class Meta:
        model  = CartItem
        fields = ['uid', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'phone', 'birth_date', 'membership'
        ]
    
    def validate_user_id(self, value):
        if value < 1:
            raise serializers.ValidationError("User ID most be positive an not equal to zero.")
        
        elif not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"User with ID {value} does not exists!")
        
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    """
        Client does not have send additional request for each product in the order.
        we only serialize a few information about the product.
    """
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'customer', 'items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id): # Ensure to cart_id exist, to stop create empty orders , without any itmes.
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No Cart with given ID was found!')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The Cart Is Empty!')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer, is_created = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) 
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        Cart.objects.filter(pk=cart_id).delete()
        return order

class UserNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

