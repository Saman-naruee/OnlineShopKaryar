from django.urls import path
from .views import *

urlpatterns = [
    path('products/', ProductList.as_view()),
    path('products/<int:pk>/', ProductDetail.as_view()),
    path('collections/', collection_list),
    path('collections/<int:pk>/', collection_detail, name='collection-detail'),
]