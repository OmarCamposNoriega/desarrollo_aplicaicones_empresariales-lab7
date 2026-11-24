"""
TECSUP - Laboratorio 07: ORM en Django
Script de demostracion y verificacion de consultas ORM.
Curso: Desarrollo de Aplicaciones Web / Empresariales
Docente: Hector Manrique Morante
Estudiante: Omar Steve Campos Noriega
"""

import os
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR if (CURRENT_DIR / 'manage.py').exists() else CURRENT_DIR / 'lab07'

sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab07.settings')

import django
django.setup()

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.utils import timezone
from tabulate import tabulate

from eventos.models import Evento, RegistroEvento, Usuario
from recetas.models import Autor, Comentario, Receta


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)


def print_section(num: str, title: str, query_code: str) -> None:
    print(f"\n[{num}] {title}")
    print("-" * 80)
    print("ORM:")
    for line in query_code.strip().split("\n"):
        print(f"  {line}")
    print("-" * 80)
    print("Resultado:")


def ejecutar_actividad_2() -> None:
    print_header("ACTIVIDAD 2: CONSULTAS ORM EN APP RECETAS")

    print_section("2.1", "Listar autores con all()", "autores = Autor.objects.all()")
    autores = Autor.objects.all()
    data = [[a.id, a.nombre, a.email] for a in autores]
    print(tabulate(data, headers=["ID", "Nombre", "Email"], tablefmt="grid"))

    print_section("2.2", "Obtener autor por clave primaria con get(pk=1)", "primer = Autor.objects.get(pk=1)")
    primer = Autor.objects.get(pk=1)
    print(f"-> ID={primer.id}, Nombre='{primer.nombre}', Email='{primer.email}'")

    print_section(
        "2.3",
        "Exclusion: recetas cuyos ingredientes no empiezan con 'A'",
        "Receta.objects.exclude(ingredientes__startswith='A')",
    )
    recetas_no_a = Receta.objects.exclude(ingredientes__startswith='A')
    data = [[r.id, r.titulo, r.ingredientes, r.autor.nombre] for r in recetas_no_a]
    print(tabulate(data, headers=["ID", "Titulo", "Ingredientes", "Autor"], tablefmt="grid"))

    print_section(
        "2.4",
        "Filtro contains sobre preparacion",
        "Receta.objects.filter(preparacion__contains='tetera')",
    )
    recetas_tetera = Receta.objects.filter(preparacion__contains='tetera')
    data = [[r.id, r.titulo, r.preparacion] for r in recetas_tetera]
    print(tabulate(data, headers=["ID", "Titulo", "Preparacion"], tablefmt="grid"))

    print_section(
        "2.5",
        "Ordenamiento con order_by() y reverse()",
        "Receta.objects.all().order_by('titulo')\nReceta.objects.all().order_by('titulo').reverse()",
    )
    ordenadas = list(Receta.objects.all().order_by('titulo').values_list('titulo', flat=True))
    invertidas = list(Receta.objects.all().order_by('titulo').reverse().values_list('titulo', flat=True))
    print(f"-> Ascendente:  {ordenadas}")
    print(f"-> Descendente: {invertidas}")

    print_section(
        "2.6",
        "Conteo de comentarios con count()",
        "r1 = Receta.objects.first()\ntotal_comentarios = r1.comentarios.count()",
    )
    r1 = Receta.objects.first()
    if r1:
        print(f"-> Receta '{r1.titulo}': {r1.comentarios.count()} comentario(s)")

    print_section(
        "2.7",
        "Navegacion de clave foranea desde Receta hacia Autor",
        "receta = Receta.objects.get(titulo='Agua Hervida')\nreceta.autor.nombre, receta.autor.email",
    )
    receta = Receta.objects.filter(titulo__icontains='Agua').first()
    if receta:
        print(f"-> Receta: {receta.titulo} | Autor: {receta.autor.nombre} ({receta.autor.email})")


def ejecutar_actividad_3() -> None:
    print_header("ACTIVIDAD 3: CONSULTAS AVANZADAS EN GESTION DE EVENTOS")
    ahora = timezone.now()

    print_section(
        "3.1",
        "Usuarios registrados por evento",
        "Evento.objects.annotate(total_usuarios=Count('registros'))",
    )
    eventos = Evento.objects.annotate(total_usuarios=Count('registros')).select_related('organizador')
    data = [
        [e.id, e.titulo, e.organizador.nombre, e.capacidad, e.total_usuarios, e.capacidad - e.total_usuarios]
        for e in eventos
    ]
    print(tabulate(data, headers=["ID", "Evento", "Organizador", "Capacidad", "Inscritos", "Disponibles"], tablefmt="grid"))

    print_section(
        "3.2",
        "Eventos programados en el mes actual",
        "Evento.objects.filter(fecha__year=ahora.year, fecha__month=ahora.month).order_by('fecha')",
    )
    eventos_mes = Evento.objects.filter(fecha__year=ahora.year, fecha__month=ahora.month).order_by('fecha')
    print(f"-> Total en {ahora.strftime('%Y-%m')}: {eventos_mes.count()} evento(s)")
    data = [[e.id, e.titulo, e.fecha.strftime('%d/%m/%Y %H:%M'), e.ubicacion] for e in eventos_mes]
    print(tabulate(data, headers=["ID", "Evento", "Fecha", "Ubicacion"], tablefmt="grid"))

    print_section(
        "3.3",
        "Usuarios mas activos por numero de inscripciones",
        "Usuario.objects.annotate(total_participaciones=Count('registros')).order_by('-total_participaciones')[:5]",
    )
    ranking = Usuario.objects.annotate(total_participaciones=Count('registros')).order_by('-total_participaciones')[:5]
    data = [[i + 1, u.nombre, u.email, u.ciudad, u.total_participaciones] for i, u in enumerate(ranking)]
    print(tabulate(data, headers=["Puesto", "Usuario", "Email", "Ciudad", "Participaciones"], tablefmt="grid"))

    print_section(
        "3.4",
        "Eventos organizados por usuario",
        "Usuario.objects.annotate(total_organizados=Count('eventos_organizados')).filter(total_organizados__gt=0)",
    )
    organizadores = (
        Usuario.objects.annotate(total_organizados=Count('eventos_organizados'))
        .filter(total_organizados__gt=0)
        .order_by('-total_organizados')
    )
    data = [[u.id, u.nombre, u.email, u.ciudad, u.total_organizados] for u in organizadores]
    print(tabulate(data, headers=["ID", "Organizador", "Email", "Ciudad", "Organizados"], tablefmt="grid"))

    print_section(
        "3.5",
        "Consulta compuesta con Q objects",
        "Evento.objects.filter((Q(titulo__icontains='Tecsup') | Q(descripcion__icontains='Django') | Q(ubicacion__icontains='Auditorio')) & Q(capacidad__gte=50)).distinct()",
    )
    eventos_q = Evento.objects.filter(
        (Q(titulo__icontains='Tecsup') | Q(descripcion__icontains='Django') | Q(ubicacion__icontains='Auditorio'))
        & Q(capacidad__gte=50)
    ).distinct()
    data = [[e.id, e.titulo, e.ubicacion, e.capacidad] for e in eventos_q]
    print(tabulate(data, headers=["ID", "Evento", "Ubicacion", "Capacidad"], tablefmt="grid"))

    print_section(
        "3.6",
        "Agregaciones estadisticas con aggregate()",
        "Evento.objects.aggregate(total_eventos=Count('id'), promedio_capacidad=Avg('capacidad'), max_capacidad=Max('capacidad'), min_capacidad=Min('capacidad'), capacidad_total=Sum('capacidad'))",
    )
    stats = Evento.objects.aggregate(
        total_eventos=Count('id'),
        promedio_capacidad=Avg('capacidad'),
        max_capacidad=Max('capacidad'),
        min_capacidad=Min('capacidad'),
        capacidad_total=Sum('capacidad'),
    )
    promedio = f"{stats['promedio_capacidad']:.1f}" if stats['promedio_capacidad'] is not None else "0.0"
    data = [
        ["Total de eventos", stats['total_eventos']],
        ["Promedio de capacidad (Avg)", f"{promedio} personas"],
        ["Capacidad maxima (Max)", f"{stats['max_capacidad']} personas"],
        ["Capacidad minima (Min)", f"{stats['min_capacidad']} personas"],
        ["Capacidad combinada (Sum)", f"{stats['capacidad_total']} personas"],
    ]
    print(tabulate(data, headers=["Metrica", "Valor"], tablefmt="grid"))


if __name__ == '__main__':
    ejecutar_actividad_2()
    ejecutar_actividad_3()
    print_header("VERIFICACION FINALIZADA")
