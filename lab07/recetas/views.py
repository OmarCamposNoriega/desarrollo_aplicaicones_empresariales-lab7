from django.shortcuts import render
from .models import Autor, Receta, Comentario


def receta_lista(request):
    """Lista de recetas y autores de la Actividad 2"""
    recetas = Receta.objects.select_related('autor').prefetch_related('comentarios').all()
    autores = Autor.objects.prefetch_related('recetas').all()

    # Demostración de filtros ORM de la Actividad 2
    recetas_no_a = Receta.objects.exclude(ingredientes__startswith='A')
    recetas_tetera = Receta.objects.filter(preparacion__contains='tetera')
    recetas_ordenadas = Receta.objects.all().order_by('titulo')

    context = {
        'recetas': recetas,
        'autores': autores,
        'recetas_no_a': recetas_no_a,
        'recetas_tetera': recetas_tetera,
        'recetas_ordenadas': recetas_ordenadas,
    }
    return render(request, 'recetas/receta_lista.html', context)
