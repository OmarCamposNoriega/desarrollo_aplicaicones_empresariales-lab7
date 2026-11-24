"""
URL configuration for lab07 project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "TECSUP - Laboratorio 07: ORM en Django"
admin.site.site_title = "Panel Administrativo Lab 07"
admin.site.index_title = "Gestión de Recetas y Eventos"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recetas/', include('recetas.urls')),
    path('', include('eventos.urls')),
]
