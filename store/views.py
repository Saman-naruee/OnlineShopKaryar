from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializer import ProductSerializer


@api_view()
def product_list(request):
    queryset = Product.objects.select_related('collection').all()
    srializer = ProductSerializer(queryset, many=True)
    return Response(srializer.data)

@api_view(['GET'])
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)