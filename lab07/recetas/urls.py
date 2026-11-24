from django.urls import path
from . import views

urlpatterns = [
    path('', views.receta_lista, name='receta_lista'),
]

