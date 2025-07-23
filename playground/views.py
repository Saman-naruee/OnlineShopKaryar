from django.shortcuts import render
from traitlets import All
from .tasks import notify_customers
import requests
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

import logging

logger = logging.getLogger(__name__)


class HelloView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(cache_page(1 * 60))
    def get(self, request):
        try:
            logger.info("Getting data form httpbin... .")
            response = requests.get('https://httpbin.org/delay/2')
            logger.info("Got response form httpbin.")
            data = response.json()
        except requests.ConnectionError:
            logger.critical("HttpBin is Offline!")
        return render(request, 'hello.html', {'name': f'{data}'})

