from email import message
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import *
from django.db.models import Value, F, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db import transaction
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage, BadHeaderError
from templated_mail.mail import BaseEmailMessage

def say_hello(request):

    try:
        message = BaseEmailMessage(
            template_name='emails/hello_email.html',
            context={
                'name': 'SMP',
                'message': 'Hi there! This is a test email.'
            },
        )
        message.send(['M8t5o@example.com'])
    except BadHeaderError as e:
        return render(request, 'hello.html', {'name': 'SMP Error', 'result': str(e)})
    queryset = Product.objects.raw('SELECT id, title FROM store_product')
    return render(request, 'hello.html', {'name': "Saman/Smtp", 'result': list(queryset)})

