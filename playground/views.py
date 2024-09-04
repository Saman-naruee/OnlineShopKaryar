from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import *
from django.db.models import Value, F, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db import transaction
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

def say_hello(request):
    queryset = Product.objects.raw('SELECT id, title FROM store_product')
    return render(request, 'hello.html', {'name': 'Saman', 'result': list(queryset)})

