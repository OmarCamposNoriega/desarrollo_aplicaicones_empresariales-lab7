from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre Completo')
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    ciudad = models.CharField(max_length=100, default='Lima', verbose_name='Ciudad')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.email})"

    def get_total_organizados(self):
        return self.eventos_organizados.count()

    def get_total_inscripciones(self):
        return self.registros.count()


class Evento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título del Evento')
    descripcion = models.TextField(verbose_name='Descripción Detallada')
    fecha = models.DateTimeField(verbose_name='Fecha y Hora del Evento')
    ubicacion = models.CharField(max_length=200, verbose_name='Ubicación / Lugar')
    capacidad = models.PositiveIntegerField(verbose_name='Capacidad Máxima')
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='eventos_organizados',
        verbose_name='Organizador'
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha']

    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    @property
    def total_inscritos(self):
        return self.registros.filter(estado='CONFIRMADO').count()

    @property
    def cupos_disponibles(self):
        disponibles = self.capacidad - self.total_inscritos
        return max(0, disponibles)

    @property
    def es_este_mes(self):
        ahora = timezone.now()
        return self.fecha.year == ahora.year and self.fecha.month == ahora.month


class RegistroEvento(models.Model):
    ESTADOS = [
        ('CONFIRMADO', 'Confirmado'),
        ('PENDIENTE', 'Pendiente'),
        ('CANCELADO', 'Cancelado'),
    ]

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='registros',
        verbose_name='Evento'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='registros',
        verbose_name='Usuario'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Inscripción')
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='CONFIRMADO',
        verbose_name='Estado del Registro'
    )
    observaciones = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Observaciones o Notas'
    )

    class Meta:
        verbose_name = 'Registro a Evento'
        verbose_name_plural = 'Registros a Eventos'
        unique_together = ('evento', 'usuario')
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.usuario.nombre} -> {self.evento.titulo} [{self.estado}]"
