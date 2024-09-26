from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermission
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer
from .serializer import ProductSerializer,\
    CollectionSerializer, ReviewSerializer, CartSerializer,\
    CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, UserProfileSerializer
from .filters import ProductFilter
from .pagination import DefaultPagination
from rest_framework.viewsets import ModelViewSet

class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    
    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'product can not be deleted, we have related orderitems!'}, 
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        products_count = Product.objects.filter(collection=collection).count() > 0
        if products_count:
            return Response({'error':'can not delete because there is products associated with this collection'},
                        status=status.HTTP_403_FORBIDDEN
                        )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin, DestroyModelMixin,
                RetrieveModelMixin, GenericViewSet, ListModelMixin):  
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
 
class CartitemViewSet(ModelViewSet):
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
    queryset = Customer.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response({'Status': 'OK'})

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
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