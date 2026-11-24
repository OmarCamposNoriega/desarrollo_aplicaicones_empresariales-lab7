from datetime import timedelta

from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import RegistroEventoForm
from .models import Evento, RegistroEvento, Usuario


class EventosORMTests(TestCase):
    """Pruebas de modelos, restricciones y consultas ORM para la app eventos."""

    def setUp(self):
        self.ahora = timezone.now()
        self.org1 = Usuario.objects.create(
            nombre='Carlos Mendoza',
            email='carlos@tecsup.edu.pe',
            ciudad='Lima',
        )
        self.org2 = Usuario.objects.create(
            nombre='Ana Torres',
            email='ana@tecsup.edu.pe',
            ciudad='Arequipa',
        )
        self.asistente1 = Usuario.objects.create(
            nombre='Luis Ramirez',
            email='luis@dev.pe',
            ciudad='Lima',
        )
        self.asistente2 = Usuario.objects.create(
            nombre='Sofia Castro',
            email='sofia@dev.pe',
            ciudad='Trujillo',
        )

        self.ev_actual = Evento.objects.create(
            titulo='Taller Django ORM Tecsup',
            descripcion='Consultas avanzadas con annotate y Q objects.',
            fecha=self.ahora,
            ubicacion='Auditorio Tecsup',
            capacidad=2,
            organizador=self.org1,
        )
        self.ev_futuro = Evento.objects.create(
            titulo='Seminario Cloud',
            descripcion='Contenedores y despliegue.',
            fecha=self.ahora + timedelta(days=40),
            ubicacion='Virtual',
            capacidad=50,
            organizador=self.org1,
        )
        self.ev_pasado = Evento.objects.create(
            titulo='Introduccion Python',
            descripcion='Fundamentos del lenguaje.',
            fecha=self.ahora - timedelta(days=40),
            ubicacion='Sala C1',
            capacidad=20,
            organizador=self.org2,
        )

        RegistroEvento.objects.create(
            evento=self.ev_actual,
            usuario=self.asistente1,
            estado='CONFIRMADO',
        )
        RegistroEvento.objects.create(
            evento=self.ev_actual,
            usuario=self.asistente2,
            estado='PENDIENTE',
        )
        RegistroEvento.objects.create(
            evento=self.ev_futuro,
            usuario=self.asistente1,
            estado='CONFIRMADO',
        )

    def test_propiedades_capacidad_y_mes(self):
        self.assertEqual(self.ev_actual.total_inscritos, 1)
        self.assertEqual(self.ev_actual.cupos_disponibles, 1)
        self.assertTrue(self.ev_actual.es_este_mes)

    def test_restriccion_registro_unico(self):
        with self.assertRaises(IntegrityError):
            RegistroEvento.objects.create(
                evento=self.ev_actual,
                usuario=self.asistente1,
                estado='CONFIRMADO',
            )

    def test_consultas_annotate_y_aggregate(self):
        activos = list(
            Usuario.objects.annotate(total_participaciones=Count('registros'))
            .order_by('-total_participaciones')
        )
        self.assertEqual(activos[0], self.asistente1)
        self.assertEqual(activos[0].total_participaciones, 2)

        organizadores = list(
            Usuario.objects.annotate(total_organizados=Count('eventos_organizados'))
            .filter(total_organizados__gt=0)
            .order_by('-total_organizados')
        )
        self.assertEqual(organizadores[0], self.org1)
        self.assertEqual(organizadores[0].total_organizados, 2)

        stats = Evento.objects.aggregate(
            total=Count('id'),
            promedio=Avg('capacidad'),
            maximo=Max('capacidad'),
            minimo=Min('capacidad'),
            suma=Sum('capacidad'),
        )
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['maximo'], 50)
        self.assertEqual(stats['minimo'], 2)
        self.assertEqual(stats['suma'], 72)

    def test_consulta_q_objects_y_filtro_mensual(self):
        eventos_mes = Evento.objects.filter(
            fecha__year=self.ahora.year,
            fecha__month=self.ahora.month,
        )
        self.assertIn(self.ev_actual, eventos_mes)

        resultado_q = Evento.objects.filter(
            (Q(titulo__icontains='Cloud') | Q(descripcion__icontains='annotate'))
            & Q(capacidad__gte=2)
        ).distinct()
        self.assertEqual(resultado_q.count(), 2)


class RegistroEventoFormTests(TestCase):
    """Pruebas de validacion de duplicados y aforo en RegistroEventoForm."""

    def setUp(self):
        self.org = Usuario.objects.create(nombre='Org', email='org@tecsup.edu.pe')
        self.u1 = Usuario.objects.create(nombre='User 1', email='u1@tecsup.edu.pe')
        self.u2 = Usuario.objects.create(nombre='User 2', email='u2@tecsup.edu.pe')
        self.evento = Evento.objects.create(
            titulo='Evento Cupo Unico',
            descripcion='Prueba de aforo',
            fecha=timezone.now(),
            ubicacion='Lima',
            capacidad=1,
            organizador=self.org,
        )
        RegistroEvento.objects.create(evento=self.evento, usuario=self.u1, estado='CONFIRMADO')

    def test_rechaza_registro_duplicado(self):
        form = RegistroEventoForm(
            data={
                'evento': self.evento.pk,
                'usuario': self.u1.pk,
                'estado': 'CONFIRMADO',
                'observaciones': '',
            }
        )
        self.assertFalse(form.is_valid())

    def test_rechaza_registro_cuando_no_hay_cupos(self):
        form = RegistroEventoForm(
            data={
                'evento': self.evento.pk,
                'usuario': self.u2.pk,
                'estado': 'CONFIRMADO',
                'observaciones': '',
            }
        )
        self.assertFalse(form.is_valid())


class EventosViewsTests(TestCase):
    """Pruebas de integracion para las vistas principales y consultas avanzadas."""

    def setUp(self):
        self.org = Usuario.objects.create(nombre='Organizador', email='org@tecsup.edu.pe')
        self.asistente = Usuario.objects.create(nombre='Asistente', email='asist@tecsup.edu.pe')
        self.evento = Evento.objects.create(
            titulo='Workshop ORM Tecsup',
            descripcion='Uso de QuerySets',
            fecha=timezone.now() + timedelta(days=2),
            ubicacion='Lima',
            capacidad=30,
            organizador=self.org,
        )

    def test_vistas_principales_responden_200(self):
        rutas = [
            reverse('inicio'),
            reverse('evento_lista'),
            reverse('evento_detalle', kwargs={'pk': self.evento.pk}),
            reverse('usuario_lista'),
            reverse('registro_lista'),
            reverse('consultas_avanzadas'),
        ]
        for ruta in rutas:
            response = self.client.get(ruta)
            self.assertEqual(response.status_code, 200)

    def test_consultas_avanzadas_tolera_evento_id_invalido(self):
        response = self.client.get(reverse('consultas_avanzadas'), {'evento_id': 'no-numerico'})
        self.assertEqual(response.status_code, 200)

    def test_inscripcion_directa_en_evento_detalle(self):
        response = self.client.post(
            reverse('evento_detalle', kwargs={'pk': self.evento.pk}),
            {'usuario': self.asistente.pk, 'observaciones': 'Confirmado'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            RegistroEvento.objects.filter(evento=self.evento, usuario=self.asistente).exists()
        )
