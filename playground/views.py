from django.shortcuts import render
from django.http import HttpResponse

def say_hello(request):
    x = 3
    y = 7
    return render(request, 'hello.html', {'value' : f'{x} != {y}'})