from django.contrib import admin
from .models import Autor, Receta, Comentario


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email')
    search_fields = ('nombre', 'email')


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'tiempo_registro')
    list_filter = ('autor', 'tiempo_registro')
    search_fields = ('titulo', 'ingredientes', 'preparacion')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'receta', 'texto')
    list_filter = ('receta',)
    search_fields = ('texto',)
