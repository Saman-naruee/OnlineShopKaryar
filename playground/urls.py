from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('task/', views.HelloView.as_view(), name='hello'),
]
