from django.urls import path
from .views import *

urlpatterns = [
    path('products/', product_list),
    path('products/<int:pk>/', product_detail),
    path('collections/', collection_list),
    path('collections/<int:pk>/', collection_detail, name='collection-detail'),
]