import os
from datetime import timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab07.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from eventos.models import Evento, RegistroEvento, Usuario
from recetas.models import Autor, Comentario, Receta


def sembrar() -> None:
    print("[INFO] Iniciando carga de datos para Laboratorio 07...")

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@tecsup.edu.pe', 'Tecsup2019')
        print("[OK] Superusuario creado: admin")
    else:
        print("[INFO] Superusuario 'admin' ya existe.")

    print("[INFO] Cargando datos de Actividad 2 (recetas)...")
    autor, _ = Autor.objects.get_or_create(
        nombre='Javier Pérez',
        defaults={'email': 'eperez@mail.com'},
    )

    r1, _ = Receta.objects.get_or_create(
        titulo='Huevito Frito',
        defaults={
            'ingredientes': 'huevo, sal, aceite',
            'preparacion': 'Calentar la sarten y freir el huevo',
            'autor': autor,
        },
    )

    Receta.objects.get_or_create(
        titulo='Agua Hervida',
        defaults={
            'ingredientes': 'agua',
            'preparacion': 'Poner la tetera en la hornilla hasta hervir',
            'autor': autor,
        },
    )

    Comentario.objects.get_or_create(receta=r1, texto='Un clásico para el desayuno')
    Comentario.objects.get_or_create(receta=r1, texto='Para pasar el hambre')
    print("[OK] Datos de recetas registrados.")

    print("[INFO] Cargando datos de Actividad 3 (eventos)...")
    usuarios_data = [
        {'nombre': 'Carlos Mendoza Ramos', 'email': 'carlos.mendoza@tecsup.edu.pe', 'telefono': '987654321', 'ciudad': 'Lima'},
        {'nombre': 'Ana Paula Torres', 'email': 'ana.torres@techperu.org', 'telefono': '976543210', 'ciudad': 'Lima'},
        {'nombre': 'Luis Alberto Ramírez', 'email': 'luis.ramirez@dev.pe', 'telefono': '965432109', 'ciudad': 'Arequipa'},
        {'nombre': 'Sofía Alejandra Castro', 'email': 'sofia.castro@gmail.com', 'telefono': '954321098', 'ciudad': 'Lima'},
        {'nombre': 'Diego Armando Fernández', 'email': 'diego.f@innovacion.pe', 'telefono': '943210987', 'ciudad': 'Trujillo'},
        {'nombre': 'Elena Beatriz Ramos', 'email': 'elena.ramos@tecsup.edu.pe', 'telefono': '932109876', 'ciudad': 'Lima'},
    ]

    usuarios_obj = {}
    for u_data in usuarios_data:
        obj, _ = Usuario.objects.get_or_create(email=u_data['email'], defaults=u_data)
        usuarios_obj[u_data['email']] = obj
    print(f"[OK] {len(usuarios_obj)} usuarios registrados.")

    ahora = timezone.now()
    eventos_data = [
        {
            'titulo': 'Cumbre de Inteligencia Artificial y Django ORM 2026',
            'descripcion': 'Conferencia sobre optimizacion de consultas SQL, ORM avanzado, anotaciones y agregacion.',
            'fecha': ahora.replace(day=15, hour=10, minute=0, second=0),
            'ubicacion': 'Auditorio Tecsup Principal (Lima)',
            'capacidad': 80,
            'organizador': usuarios_obj['carlos.mendoza@tecsup.edu.pe'],
        },
        {
            'titulo': 'Taller Avanzado de Bases de Datos y PostgreSQL',
            'descripcion': 'Sesion practica con queries complejas, Q objects, transacciones y modelado relacional.',
            'fecha': ahora.replace(day=22, hour=16, minute=30, second=0),
            'ubicacion': 'Laboratorio 402 - Pabellon B Tecsup',
            'capacidad': 45,
            'organizador': usuarios_obj['ana.torres@techperu.org'],
        },
        {
            'titulo': 'Hackathon Nacional de Desarrollo Web Empresarial',
            'descripcion': 'Competencia de 24 horas para construir aplicaciones web con Django y APIs REST.',
            'fecha': ahora.replace(day=28, hour=9, minute=0, second=0),
            'ubicacion': 'Auditorio Magna Tecsup',
            'capacidad': 120,
            'organizador': usuarios_obj['carlos.mendoza@tecsup.edu.pe'],
        },
        {
            'titulo': 'Seminario de Arquitectura Cloud y Microservicios',
            'descripcion': 'Despliegues en contenedores Docker, CI/CD y escalabilidad horizontal de servicios backend.',
            'fecha': (ahora + timedelta(days=45)).replace(hour=14, minute=0),
            'ubicacion': 'Virtual Zoom / YouTube Live',
            'capacidad': 200,
            'organizador': usuarios_obj['carlos.mendoza@tecsup.edu.pe'],
        },
        {
            'titulo': 'Bootcamp Introductorio a Python y Git',
            'descripcion': 'Fundamentos de Python y control de versiones con Git y GitHub.',
            'fecha': (ahora - timedelta(days=35)).replace(hour=11, minute=0),
            'ubicacion': 'Sala de Computo C1',
            'capacidad': 35,
            'organizador': usuarios_obj['ana.torres@techperu.org'],
        },
    ]

    eventos_obj = []
    for ev_data in eventos_data:
        ev, _ = Evento.objects.get_or_create(titulo=ev_data['titulo'], defaults=ev_data)
        eventos_obj.append(ev)
    print(f"[OK] {len(eventos_obj)} eventos registrados.")

    registros_data = [
        (eventos_obj[0], usuarios_obj['luis.ramirez@dev.pe'], 'CONFIRMADO', 'Interesado en deep learning'),
        (eventos_obj[0], usuarios_obj['sofia.castro@gmail.com'], 'CONFIRMADO', 'Participante recurrente'),
        (eventos_obj[0], usuarios_obj['diego.f@innovacion.pe'], 'CONFIRMADO', 'Viene desde Trujillo'),
        (eventos_obj[0], usuarios_obj['elena.ramos@tecsup.edu.pe'], 'CONFIRMADO', 'Estudiante Tecsup C4'),
        (eventos_obj[1], usuarios_obj['luis.ramirez@dev.pe'], 'CONFIRMADO', 'Requiere certificado'),
        (eventos_obj[1], usuarios_obj['sofia.castro@gmail.com'], 'CONFIRMADO', 'Asistente confirmado'),
        (eventos_obj[1], usuarios_obj['elena.ramos@tecsup.edu.pe'], 'PENDIENTE', 'Pendiente de confirmacion'),
        (eventos_obj[2], usuarios_obj['luis.ramirez@dev.pe'], 'CONFIRMADO', 'Lider de equipo'),
        (eventos_obj[2], usuarios_obj['diego.f@innovacion.pe'], 'CONFIRMADO', 'Desarrollador backend'),
        (eventos_obj[2], usuarios_obj['sofia.castro@gmail.com'], 'CONFIRMADO', 'Disenadora UI/UX'),
        (eventos_obj[3], usuarios_obj['luis.ramirez@dev.pe'], 'CONFIRMADO', 'Asistencia virtual'),
        (eventos_obj[3], usuarios_obj['ana.torres@techperu.org'], 'CONFIRMADO', 'Ponente invitada'),
        (eventos_obj[4], usuarios_obj['elena.ramos@tecsup.edu.pe'], 'CONFIRMADO', 'Asistencia registrada'),
        (eventos_obj[4], usuarios_obj['luis.ramirez@dev.pe'], 'CONFIRMADO', 'Evaluacion aprobada'),
        (eventos_obj[4], usuarios_obj['sofia.castro@gmail.com'], 'CONFIRMADO', 'Proyectos completados'),
    ]

    for ev, usr, est, obs in registros_data:
        RegistroEvento.objects.get_or_create(
            evento=ev,
            usuario=usr,
            defaults={'estado': est, 'observaciones': obs},
        )

    print(f"[OK] {len(registros_data)} inscripciones procesadas.")
    print("[OK] Carga de datos finalizada.")


if __name__ == '__main__':
    sembrar()
