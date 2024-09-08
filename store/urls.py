from django.urls import path
from .views import *

urlpatterns = [
    path('products/', product_list),
    path('products/<int:id>/', product_detail),
]