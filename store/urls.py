from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewset)
router.register('collections', CollectionViewSet)
urlpatterns = router.urls 
