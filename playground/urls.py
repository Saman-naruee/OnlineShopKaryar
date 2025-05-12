from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('task/', views.say_hello)
]
