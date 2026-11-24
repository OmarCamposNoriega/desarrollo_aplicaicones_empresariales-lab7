from django.contrib import admin
from .models import Usuario, Evento, RegistroEvento


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'telefono', 'ciudad', 'fecha_registro')
    search_fields = ('nombre', 'email', 'ciudad')
    list_filter = ('ciudad', 'fecha_registro')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'fecha', 'ubicacion', 'capacidad', 'organizador', 'total_inscritos', 'cupos_disponibles')
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    list_filter = ('fecha', 'ubicacion', 'organizador')
    date_hierarchy = 'fecha'


@admin.register(RegistroEvento)
class RegistroEventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'usuario', 'fecha_registro', 'estado')
    list_filter = ('estado', 'fecha_registro', 'evento')
    search_fields = ('usuario__nombre', 'usuario__email', 'evento__titulo')
