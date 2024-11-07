from django.urls import path
from .views import *
from rest_framework_nested import routers
from rest_framework_nested.routers import NestedDefaultRouter

router = routers.DefaultRouter()
router.register('products', ProductViewset, basename='products')
router.register('collections', CollectionViewSet)
router.register('carts', CartViewSet)
router.register('customers', CustomViewSet)
router.register('orders', OrderViewSet, basename='orders') # basename : required when overriding get_queryset instead of queryset, cause drf can not feagure out.
router.register('notifications', NotificationViewSet, basename='notifications')


products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')
products_router.register('images', ProductImageViewSet, basename='product-image')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartitemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls

