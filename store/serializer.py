from operator import truediv
from typing import override
from django.db import transaction
from rest_framework.reverse import reverse
from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection , Review, Cart, CartItem, \
      Customer, Order, OrderItem, Notification, ProductImages
from core.models import User
from django.utils.text import slugify
from store.test_tools.tools import custom_log


class CollectionSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Collection  
        fields = ['id', 'title', 'products_count', 'products_link' ]
    
    products_count = serializers.IntegerField(read_only=True)
    products_link = serializers.SerializerMethodField(method_name='get_products_link')

    def get_products_link(self, obj):
        request = self.context.get('request')
        url = reverse('products-list', request=request)
        return f'{url}?collection_id={obj.id}'
    
    def validate_title(self, value):
        if Collection.objects.filter(title=value).exists():
            raise serializers.ValidationError('Collection with this title already exists!')
        return value
    
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
            'inventory', 'price_with_tax', 'collection', 'images', 'collection_title', 
            'collection_id',
            ] # we can keep other non-existing fields down the bottom like before.
        
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection-detail',
        lookup_field='pk',
        required=False, # for display
    )

    collection_title = serializers.SerializerMethodField(method_name='get_collection_title')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection_id = serializers.IntegerField(write_only=True)

    def get_collection_title(self, product: Product):
        return product.collection.title

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.09)   # .quantize(Decimal('0.01'))

    def validate(self, attrs):
        if not attrs.get('slug'):
            attrs['slug'] = slugify(attrs['title'])
        return attrs
    
    def create(self, validated_data):
        collection_id = validated_data.pop('collection_id')
        collection = Collection.objects.get(id=collection_id)
        validated_data['collection'] = collection
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'rating', 'user', 'description']
        read_only_fields = ['date', 'user', 'id']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not user.is_superuser and instance.user != user:
            raise serializers.ValidationError('You do not have permission to update this review')
        return super().update(instance, validated_data)


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
    """
    Serializer for notification instances.
    - Staff users can create and update notifications for any user.
    - Regular users can only view their own notifications.
    """
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_admin', 'user_username']
        read_only_fields = ['id', 'created_at', 'is_admin', 'user_username']

    
    user_username = serializers.SerializerMethodField(method_name='get_user_username')
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,  
        required=False
    )

    def get_user_username(self, notification: Notification):
        return notification.user.username
    
    def update(self, instance, validated_data):
        if 'user' in validated_data:
            raise serializers.ValidationError({"user": "User cannot be changed once notification is created."})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


    def validate(self, attrs):
        """
        validate notifications creation:
        - Staff users can create and update notifications for any user.
        - Regular users can only view their own notifications.
        - Staff must specify target user.
        - User cannot be changed once notification is created.
        """

        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError({"detail": "Authentication is required!"})
        
        if self.instance:
            # Update an instance
            if 'user' in attrs and attrs['user'] != self.instance.user:
                raise serializers.ValidationError({"user": "User cannot be changed once notification is created."})
        else:
            # Create a new instance
            if not request.user.is_staff:
                raise serializers.ValidationError({"detail": "Only staff users can create notifications for any user."})

            if not attrs.get('user'):
                raise serializers.ValidationError({"detail": "Target user must be specified."})
        
        return attrs
    

