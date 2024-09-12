from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.views import APIView
from .models import Product, Collection, OrderItem, Review
from .serializer import ProductSerializer, CollectionSerializer, ReviewSerializer
from .filters import ProductFilter

from rest_framework.viewsets import ModelViewSet

class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    
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