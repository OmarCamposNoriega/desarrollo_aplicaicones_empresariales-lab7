from django.urls import path
from . import views

urlpatterns = [
    # Inicio y Dashboard
    path('', views.inicio, name='inicio'),
    path('consultas-avanzadas/', views.consultas_avanzadas, name='consultas_avanzadas'),

    # Eventos CRUD
    path('eventos/', views.evento_lista, name='evento_lista'),
    path('eventos/crear/', views.evento_crear, name='evento_crear'),
    path('eventos/<int:pk>/', views.evento_detalle, name='evento_detalle'),
    path('eventos/<int:pk>/editar/', views.evento_editar, name='evento_editar'),
    path('eventos/<int:pk>/eliminar/', views.evento_eliminar, name='evento_eliminar'),

    # Usuarios CRUD
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/crear/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='usuario_eliminar'),

    # Registros a Eventos
    path('registros/', views.registro_lista, name='registro_lista'),
    path('registros/crear/', views.registro_crear, name='registro_crear'),
    path('registros/<int:pk>/eliminar/', views.registro_eliminar, name='registro_eliminar'),
]

