from typing import override
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from core.models import User
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermission, NotificationsPermission
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser, AllowAny
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Product, Collection, OrderItem, Review, Cart, \
    CartItem, Customer, Order, Notification, ProductImages

from .serializer import ProductSerializer,\
    CollectionSerializer, ReviewSerializer, CartSerializer,\
    CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer,\
    UserProfileSerializer, OrderListSerializer, UserNotificationsSerializer, \
    CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
from .filters import ProductFilter
from .pagination import DefaultPagination
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .exceptions import InvalidOrderException, ProductNotFoundError, CollectionNotFoundError, \
    InvalidInventoryError, DuplicateReviewError, ProductDeletionError

# User = get_user_model()


class ProductViewset(ModelViewSet):
    """
    A viewset for viewing and editing product instances.
    """
    # queryset = Product.objects.prefetch_related('images').all() # To decrease the number of queries of the database, grab images of each product.
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAdminOrReadOnly] # IsAuthenticated
    
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('images').all()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset
    
    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            raise ProductDeletionError("Cannot delete a product that is associated with an order item.")
        return super().destroy(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        data = request.data
        if 'inventory' in data and data['inventory'] < 0:
            raise InvalidInventoryError("Inventory can not be negative.")
        if 'unit_price' in data and data['unit_price'] < 0:
            raise InvalidInventoryError("Unit price can not be negative.")
        return super().update(request, *args, **kwargs)
    

class CollectionViewSet(ModelViewSet):
    """
    A viewset for performing CRUD operations on Collection instances.
    Provides endpoints for listing, creating, retrieving, updating, and deleting collections.
    Includes custom logic for creation to prevent duplicate titles and for deletion
    to prevent removing collections that still have associated products.
    """
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        if Collection.objects.filter(title=request.data['title']).exists():
            return Response({'error': 'Collection with this title already exists.'}, status=400)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        products_count = Product.objects.filter(collection=collection).count() > 0
        if products_count:
            return Response({'error':'can not delete because there is products associated with this collection'},
                        status=status.HTTP_409_CONFLICT
                        )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    """
    A viewset for viewing and editing review instances.
    """
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def create(self, request, *args, **kwargs):
        try:
            product_id = self.kwargs['product_pk']
            if Review.objects.filter(product_id=product_id, user=request.user).exists(): #Review.objects.get(product_id=product_id, user=request.user)
                raise DuplicateReviewError(
                    detail="You have already left a review for this product.",
                )
            return super().create(request, *args, **kwargs)
        except Product.DoesNotExist:
            raise ProductNotFoundError(
                detail=f'Product with id {product_id} does not exist.',
            )


class CartViewSet(CreateModelMixin, DestroyModelMixin,
                RetrieveModelMixin, GenericViewSet, ListModelMixin):
    """
    A viewset for viewing and editing cart instances.
    """
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
 
class CartitemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing cart item instances.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'POST': 
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']} # pass to serializer for using cart_id from url.

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class CustomViewSet(ModelViewSet):
    """
    A viewset for viewing and editing customer instances.
    """
    queryset = Customer.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response({'Status': 'OK'})
 
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request): # this is for user profile, and 'me' shows 
        customer, is_created = Customer.objects.get_or_create(user_id=request.user.id)
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        if request.method == 'GET':
            serializer = UserProfileSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    """
    A viewset for viewing and editing order instances.
    """
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context = {
                'user_id': self.request.user.id
                }
            )
        
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderListSerializer
 
    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_staff:
            return Order.objects.all()
        
        # customer_id is not included in the json web token and we have to calculate it from user id:
        customer_id, created = Customer.objects.only('id').get_or_create(user_id=current_user.id)
        return Order.objects.filter(customer_id=customer_id)

class NotificationViewSet(ModelViewSet):
    """
    A viewset for managing notifications.

    Only staff users can create, update, or delete notifications.
    Regular users can only read their own notifications.
    Supports filtering by last received timestamp.
    """
    serializer_class = UserNotificationsSerializer
    permission_classes = [IsAuthenticated, NotificationsPermission]

    def get_queryset(self): 
        """
        Filter notifications:
        - staff users can see all notification blong to all users
        - regular users can only see their own notifications
        - optionally filter by last received timestamp.
        """
        
        if self.request.user.is_staff:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(user=self.request.user)
        
        last_received = self.request.query_params.get('LastReceived')
        if last_received:
            last_received = timezone.datetime.fromisoformat(last_received)
            queryset = queryset.filter(created_at__gt=last_received)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        When creating a notification:
        - Admin users can create notifications for any user
        - The target user is specified in the request data
        """
        if self.request.user.is_staff:
            # Get the target user from the request data
            user_id = self.request.data.get('user')
            if user_id:
                try:
                    from core.models import User
                    user = User.objects.get(id=user_id)
                    is_admin = self.request.data.get('is_admin', True)
                    serializer.save(user=user, is_admin=is_admin)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"user": "User with this ID does not exist."})
            else:
                raise serializers.ValidationError({"user": "Target user must be specified."})
        else:
            # Regular users can only create notifications for themselves
            serializer.save(user=self.request.user)

class ProductImageViewSet(ModelViewSet):
    """
    A viewset for viewing and editing product image instances.
    """
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImages.objects.filter(product_id=self.kwargs['product_pk']) # to get product_pk from url: <-
    
    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk'], 'request': self.request}
