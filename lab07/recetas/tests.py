from django.test import TestCase
from django.urls import reverse

from .models import Autor, Comentario, Receta


class RecetasORMTests(TestCase):
    """Pruebas de consultas ORM y vista para la app recetas."""

    def setUp(self):
        self.autor = Autor.objects.create(nombre='Javier Perez', email='eperez@mail.com')
        self.r1 = Receta.objects.create(
            titulo='Huevito Frito',
            ingredientes='huevo, sal, aceite',
            preparacion='Calentar la sarten y freir',
            autor=self.autor,
        )
        self.r2 = Receta.objects.create(
            titulo='Agua Hervida',
            ingredientes='agua',
            preparacion='Poner la tetera en la hornilla',
            autor=self.autor,
        )
        Comentario.objects.create(receta=self.r1, texto='Clasico para el desayuno')

    def test_filtros_y_ordenamiento_orm(self):
        sin_a = list(Receta.objects.exclude(ingredientes__startswith='a'))
        self.assertEqual(sin_a, [self.r1])

        con_tetera = list(Receta.objects.filter(preparacion__contains='tetera'))
        self.assertEqual(con_tetera, [self.r2])

        ordenadas = list(Receta.objects.order_by('titulo').values_list('titulo', flat=True))
        self.assertEqual(ordenadas, ['Agua Hervida', 'Huevito Frito'])
        self.assertEqual(self.r1.comentarios.count(), 1)
        self.assertEqual(self.r2.autor.email, 'eperez@mail.com')

    def test_vista_receta_lista(self):
        response = self.client.get(reverse('receta_lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agua Hervida')
