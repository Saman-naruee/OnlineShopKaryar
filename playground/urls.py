from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('email/', views.say_hello)
]
