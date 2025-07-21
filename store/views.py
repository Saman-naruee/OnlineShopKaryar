from typing import override
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from colorama import Fore
from httpx import get

from core.models import User
from store.test_tools.tools import custom_logger
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, IsCartItemOwner, IsCartOwner, ViewCustomerHistoryPermission, NotificationsPermission
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser, AllowAny
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.exceptions import PermissionDenied
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
    A viewset for managing product operations in the store.

    This viewset provides CRUD operations for Product models with additional features:
    - Filtering products by collection, price range, and other attributes
    - Searching products by title and description 
    - Ordering products by price and last update date
    - Pagination support
    - Image management for products
    - Inventory validation
    - Protection against deleting products with existing orders

    Endpoints:
        GET /products/ - List all products with optional filters
        POST /products/ - Create a new product (admin only)
        GET /products/{id}/ - Retrieve a specific product
        PUT/PATCH /products/{id}/ - Update a product (admin only)
        DELETE /products/{id}/ - Delete a product (admin only)

    Attributes:
        filter_backends (list): Configures DjangoFilterBackend for filtering, SearchFilter 
            for search, and OrderingFilter for sorting results
        permission_classes (list): [IsAdminOrReadOnly] - Allow read access to all users 
            but restrict create/update/delete to admin users
        search_fields (list): Fields that can be searched ('title', 'description')
        ordering_fields (list): Fields that can be used for sorting results
        filterset_class (ProductFilter): Custom filter class for advanced filtering
        pagination_class (DefaultPagination): Handles result pagination
        serializer_class (ProductSerializer): Handles product data serialization
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
        """
        Returns an optimized queryset of products with optional collection filtering.

        This method:
        1. Prefetches related product images to minimize database queries
        2. Applies collection filtering if collection_id is provided in query params
        3. Returns all products if no collection filter is specified

        Returns:
            QuerySet: A queryset of Product instances with prefetched images

        Example:
            GET /products/?collection_id=1 - Returns products in collection 1
            GET /products/ - Returns all products
        """
        queryset = Product.objects.prefetch_related('images').all()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset
    
    def get_serializer_context(self):
        """
        Returns the context dictionary that will be passed to the serializer.
        
        The context includes:
        - request: The current HTTP request object for accessing request data
        - view: The current view instance
        - format: The requested data format
        - product_images: The related product images if any

        This context data helps the serializer properly handle URLs, permissions,
        and related data during serialization.

        Returns:
            dict: A dictionary containing context data for the serializer
        """
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        """
        Handles product deletion with order validation.

        Prevents deletion of products that have associated order items to maintain
        data integrity and order history. Only admin users can delete products.

        Args:
            request (Request): The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments including 'pk' for product ID

        Returns:
            Response: Empty response with 204 status on successful deletion

        Raises:
            ProductDeletionError: If product has associated order items
            PermissionDenied: If user is not an admin
            NotFound: If product does not exist

        Example:
            DELETE /products/1/ - Deletes product with ID 1 if possible
        """
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            raise ProductDeletionError("Cannot delete a product that is associated with an order item.")
        return super().destroy(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        """
        Handles the update of a product instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
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

    Attributes:
        queryset (QuerySet): The queryset for this viewset.
        serializer_class (class): The serializer class to use for this viewset.
        permission_classes (list): A list of permission classes to use for this viewset.

    Methods:
        create: Handles the creation of a collection instance.
        destroy: Handles the deletion of a collection instance.
    """
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a collection instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
        if Collection.objects.filter(title=request.data['title']).exists():
            return Response({'error': 'Collection with this title already exists.'}, status=400)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Handles the deletion of a collection instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
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

    Provides endpoints for listing, creating, retrieving, updating, and deleting reviews.
    Includes custom logic for creation to prevent duplicate reviews and for deletion
    to prevent removing reviews that still have associated products.

    Attributes:
        serializer_class (class): The serializer class to use for this viewset.
        permission_classes (list): A list of permission classes to use for this viewset.

    Methods:
        get_queryset: Returns the queryset for this viewset.
        get_serializer_context: Returns the serializer context for this viewset.
        update: Handles the update of a review instance.
        destroy: Handles the deletion of a review instance.
        perform_create: Handles the creation of a review instance.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns the queryset for this viewset.

        Returns:
            QuerySet: The queryset for this viewset.
        """
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        """
        Returns the serializer context for this viewset.

        Returns:
            dict: The serializer context for this viewset.
        """
        return {'product_id': self.kwargs['product_pk']}
    
    def update(self, request, *args, **kwargs):
        """
        Handles the update of a review instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
        review = self.get_object()
        if not review.user == self.request.user:
            raise serializers.ValidationError({'detail': 'You do not have permission to update this review.'}, status=403)
    
    def destroy(self, request, *args, **kwargs):
        """
        Handles the deletion of a review instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
        review = self.get_object()
        if not review.user == self.request.user or not request.user.is_staff:
            raise serializers.ValidationError({'detail': 'You do not have permission to delete this review.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Handles the creation of a review instance.

        Args:
            serializer (Serializer): The serializer object.

        Returns:
            Response: The response object.
        """
        product_id = self.kwargs['product_pk']

        # Check if product exists
        product = get_object_or_404(Product, pk=product_id)

        # Check for existing review by the user
        if Review.objects.filter(product=product, user=self.request.user).exists():
            raise DuplicateReviewError(
                detail="You have already left a review for this product.",
            )
        serializer.save(user=self.request.user, product=product)


class CartViewSet(CreateModelMixin, DestroyModelMixin,
                RetrieveModelMixin, GenericViewSet, ListModelMixin):
    
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]  # Allow any authenticated user

    def get_queryset(self):
        # Only return carts belonging to the current user
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 
class CartItemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing cart item instances.

    Provides endpoints for listing, creating, retrieving, updating, and deleting cart items.

    Attributes:
        http_method_names (list): A list of HTTP methods to use for this viewset.
        serializer_class (class): The serializer class to use for this viewset.

    Methods:
        get_serializer_class: Returns the serializer class for this viewset.
        get_serializer_context: Returns the serializer context for this viewset.
        get_queryset: Returns the queryset for this viewset.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsCartItemOwner]
    
    def get_serializer_class(self):
        """
        Returns the serializer class for this viewset.

        Returns:
            class: The serializer class for this viewset.
        """
        if self.request.method == 'POST': 
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        """
        Returns the serializer context for this viewset.

        Returns:
            dict: The serializer context for this viewset.
        """
        return {'cart_id': self.kwargs['cart_pk'], 'request': self.request} # pass to serializer for using cart_id from url.

    def get_queryset(self):
        """
        Returns the queryset for this viewset.

        Returns:
            QuerySet: The queryset for this viewset.
        """
        cart_id = self.kwargs['cart_pk']
        # Verify that the cart belongs to current user
        cart = get_object_or_404(Cart, pk=cart_id, user=self.request.user)
        return CartItem.objects.filter(cart_id=cart_id).select_related('product')
    
    def get_cart(self):
        """
        Returns the cart for this viewset.
        """
        cart_id = self.kwargs['cart_pk']
        cart = get_object_or_404(Cart, pk=cart_id)

        # Check cart's ownership
        if cart.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this cart.")
        return cart
    
    def perform_create(self, serializer):
        cart = self.get_cart()
        serializer.save(cart=cart)


class CustomViewSet(ModelViewSet):
    """
    A viewset for viewing and editing customer instances.

    Provides endpoints for listing, creating, retrieving, updating, and deleting customers.

    Attributes:
        queryset (QuerySet): The queryset for this viewset.
        serializer_class (class): The serializer class to use for this viewset.
        permission_classes (list): A list of permission classes to use for this viewset.

    Methods:
        history: Handles the history of a customer instance.
        me: Handles the current user's customer instance.
    """
    queryset = Customer.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        """
        Handles the history of a customer instance.

        Args:
            request (Request): The request object.
            pk (int): The primary key of the customer instance.

        Returns:
            Response: The response object.
        """
        return Response({'Status': 'OK'})
 
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request): # this is for user profile, and 'me' shows 
        """
        Handles the current user's customer instance.

        Args:
            request (Request): The request object.

        Returns:
            Response: The response object.
        """
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

    Provides endpoints for listing, creating, retrieving, updating, and deleting orders.

    Attributes:
        http_method_names (list): A list of HTTP methods to use for this viewset.
        permission_classes (list): A list of permission classes to use for this viewset.

    Methods:
        get_permissions: Returns the permission classes for this viewset.
        create: Handles the creation of an order instance.
        get_serializer_class: Returns the serializer class for this viewset.
        get_queryset: Returns the queryset for this viewset.
    """
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        """
        Returns the permission classes for this viewset.

        Returns:
            list: A list of permission classes for this viewset.
        """
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of an order instance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object.
        """
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
        """
        Returns the serializer class for this viewset.

        Returns:
            class: The serializer class for this viewset.
        """
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderListSerializer
 
    def get_queryset(self):
        """
        Returns the queryset for this viewset.

        Returns:
            QuerySet: The queryset for this viewset.
        """
        current_user = self.request.user
        if current_user.is_staff:
            return Order.objects.all()
        
        # customer_id is not included in the json web token and we have to calculate it from user id:
        customer_id, created = Customer.objects.only('id').get_or_create(user_id=current_user.id)
        return Order.objects.filter(customer_id=customer_id)

class NotificationViewSet(ModelViewSet):
    """
    A viewset for managing notifications.

    Provides endpoints for listing, creating, retrieving, updating, and deleting notifications.

    Attributes:
        serializer_class (class): The serializer class to use for this viewset.
        permission_classes (list): A list of permission classes to use for this viewset.

    Methods:
        get_queryset: Returns the queryset for this viewset.
        perform_create: Handles the creation of a notification instance.
    """
    serializer_class = UserNotificationsSerializer
    permission_classes = [IsAuthenticated, NotificationsPermission]

    def get_queryset(self): 
        """
        Returns the queryset for this viewset.

        Returns:
            QuerySet: The queryset for this viewset.
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
        Handles the creation of a notification instance.

        Args:
            serializer (Serializer): The serializer object.

        Returns:
            Response: The response object.
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

    Provides endpoints for listing, creating, retrieving, updating, and deleting product images.

    Attributes:
        serializer_class (class): The serializer class to use for this viewset.

    Methods:
        get_queryset: Returns the queryset for this viewset.
        get_serializer_context: Returns the serializer context for this viewset.
    """
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        """
        Returns the queryset for this viewset.

        Returns:
            QuerySet: The queryset for this viewset.
        """
        return ProductImages.objects.filter(product_id=self.kwargs['product_pk']) # to get product_pk from url: <-
    
    def get_serializer_context(self):
        """
        Returns the serializer context for this viewset.

        Returns:
            dict: The serializer context for this viewset.
        """
        return {'product_pk': self.kwargs['product_pk'], 'request': self.request}
