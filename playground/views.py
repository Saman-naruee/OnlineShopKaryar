from django.shortcuts import render
from .tasks import notify_customers
import requests


def say_hello(request):
    requests.get("https://httpbin.org/delay/3")
    # notify_customers.delay("Hello Celery!")
    return render(request, 'hello.html', {'name': "Samantha"})

