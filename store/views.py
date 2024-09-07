from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product


@api_view()
def product_list(request):
    products = Product.objects.all()
    data = {
        'products': list(products.values('title', 'unit_price', 'inventory'))[:4]
    }
    return Response(data)

@api_view(['GET'])
def product_detail(request, id):
    try:
        product = Product.objects.get(pk=id)
        data = {
            'title': product.title,
            'description': product.description
        }
        return Response(data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)