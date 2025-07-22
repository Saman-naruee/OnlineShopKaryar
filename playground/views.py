from django.shortcuts import render
from django.core.cache import cache
from .tasks import notify_customers
import requests


def say_hello(request):
    key = 'httpbin_result'
    result = cache.get(key)
    if result is None:
        response = requests.get('https://httpbin.org/delay/2')
        data = response.json()
        cache.set(key, data)
    return render(request, 'hello.html', {'name': f"#\n{result}"})

