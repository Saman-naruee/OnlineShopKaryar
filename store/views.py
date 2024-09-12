from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.views import APIView
from .models import Product, Collection, OrderItem
from .serializer import ProductSerializer, CollectionSerializer

from rest_framework.viewsets import ModelViewSet

class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if OrderItem.objects.filter(product=product).exists():
            return Response({'error': 'product can not be deleted, we have orderitems!'}, 
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        products_count = Product.objects.filter(collection=collection).count()
        if products_count > 0:
            return Response({'error':'can not delete because there is products associated with this collection'},
                        status=status.HTTP_403_FORBIDDEN
                        )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 # Using viewsets for combine multiple related viws inside a single class: it is a set of related views.

class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if OrderItem.objects.filter(product=product).exists():
            return Response({'error': 'product can not be deleted, we have orderitems!'}, 
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        products_count = Product.objects.filter(collection=collection).count()
        if products_count > 0:
            return Response({'error':'can not delete because there is products associated with this collection'},
                        status=status.HTTP_403_FORBIDDEN
                        )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
