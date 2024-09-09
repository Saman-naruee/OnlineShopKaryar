from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection
from .serializer import ProductSerializer, CollectionSerializer


@api_view()
def product_list(request):
    queryset = Product.objects.select_related('collection').all()
    srializer = ProductSerializer(queryset, many=True, context = {'request': request})
    return Response(srializer.data)

@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view()
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    serializer = CollectionSerializer(collection, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)