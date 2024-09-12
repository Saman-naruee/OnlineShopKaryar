from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewset)
router.register('collections', CollectionViewSet)
urlpatterns = router.urls 


# urlpatterns = [ 
    # path('products/', ProductList.as_view()),
    # path('products/<int:pk>/', ProductDetail.as_view()),
    # path('collections/', CollectionList.as_view()),
    # path('collections/<int:pk>/', CollectionDetail.as_view()),
# ]