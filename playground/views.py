from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import *
from django.db.models import Value, F, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db import transaction
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins, mail_managers, send_mail, BadHeaderError

def say_hello(request):
    try:
        send_mail(
            'smtp testing',
            'Hi there, this is the first email sent from smtp',
            'narueesaman@gmail.com',
            ['samannaruee@gmail.com'],
        )
    except BadHeaderError as e:
        return render(request, 'hello.html', {'name': 'SMP Error', 'result': str(e)})
    queryset = Product.objects.raw('SELECT id, title FROM store_product')
    return render(request, 'hello.html', {'name': 'Saman', 'result': list(queryset)})

