from django.urls import path
from .views import *
from rest_framework_nested import routers
from rest_framework_nested.routers import NestedDefaultRouter

router = routers.DefaultRouter()
router.register('products', ProductViewset, basename='products')
router.register('collections', CollectionViewSet)
router.register('cart', CartViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')
urlpatterns = router.urls + products_router.urls
