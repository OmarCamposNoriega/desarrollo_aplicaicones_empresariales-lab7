from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Avg, Max, Min, Sum, Q, F
from django.utils import timezone
from .models import Evento, Usuario, RegistroEvento
from .forms import EventoForm, UsuarioForm, RegistroEventoForm, InscripcionDirectaForm


def inicio(request):
    """Página principal del portal del laboratorio"""
    ahora = timezone.now()
    total_eventos = Evento.objects.count()
    total_usuarios = Usuario.objects.count()
    total_registros = RegistroEvento.objects.count()
    eventos_mes = Evento.objects.filter(fecha__year=ahora.year, fecha__month=ahora.month).count()
    proximos_eventos = (
        Evento.objects.select_related('organizador')
        .filter(fecha__gte=ahora)
        .order_by('fecha')[:3]
    )

    context = {
        'total_eventos': total_eventos,
        'total_usuarios': total_usuarios,
        'total_registros': total_registros,
        'eventos_mes': eventos_mes,
        'proximos_eventos': proximos_eventos,
    }
    return render(request, 'eventos/inicio.html', context)


# ==========================================
# CRUD DE EVENTOS
# ==========================================

def evento_lista(request):
    """Lista de eventos con filtros dinámicos mediante Q objects"""
    eventos = Evento.objects.select_related('organizador').annotate(
        inscritos_confirmados=Count('registros', filter=Q(registros__estado='CONFIRMADO'))
    )

    # Filtro de búsqueda con Q objects (título, descripción o ubicación)
    query = request.GET.get('q', '').strip()
    if query:
        eventos = eventos.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ubicacion__icontains=query) |
            Q(organizador__nombre__icontains=query)
        )

    # Filtro por temporalidad (este mes, próximos, pasados)
    temporalidad = request.GET.get('tiempo', '')
    ahora = timezone.now()
    if temporalidad == 'este_mes':
        eventos = eventos.filter(fecha__year=ahora.year, fecha__month=ahora.month)
    elif temporalidad == 'proximos':
        eventos = eventos.filter(fecha__gte=ahora)
    elif temporalidad == 'pasados':
        eventos = eventos.filter(fecha__lt=ahora)

    # Filtro por organizador
    organizador_id = request.GET.get('organizador')
    if organizador_id:
        eventos = eventos.filter(organizador_id=organizador_id)

    organizadores = Usuario.objects.annotate(
        cant_org=Count('eventos_organizados')
    ).filter(cant_org__gt=0)

    context = {
        'eventos': eventos,
        'query': query,
        'temporalidad': temporalidad,
        'organizador_id': organizador_id,
        'organizadores': organizadores,
        'total_encontrados': eventos.count(),
    }
    return render(request, 'eventos/evento_lista.html', context)


def evento_detalle(request, pk):
    """Detalle de un evento, asistentes y formulario rápido de inscripción"""
    evento = get_object_or_404(
        Evento.objects.select_related('organizador'),
        pk=pk
    )
    registros = evento.registros.select_related('usuario').all()
    form_inscripcion = InscripcionDirectaForm()

    if request.method == 'POST':
        form_inscripcion = InscripcionDirectaForm(request.POST)
        if form_inscripcion.is_valid():
            usuario = form_inscripcion.cleaned_data['usuario']
            observaciones = form_inscripcion.cleaned_data['observaciones']

            # Validar si ya está registrado
            if RegistroEvento.objects.filter(evento=evento, usuario=usuario).exists():
                messages.warning(request, f"El usuario {usuario.nombre} ya se encuentra registrado en este evento.")
            elif evento.cupos_disponibles <= 0:
                messages.error(request, f"El evento alcanzó su capacidad máxima ({evento.capacidad}).")
            else:
                RegistroEvento.objects.create(
                    evento=evento,
                    usuario=usuario,
                    estado='CONFIRMADO',
                    observaciones=observaciones
                )
                messages.success(request, f"Inscripción registrada para {usuario.nombre}.")
                return redirect('evento_detalle', pk=pk)

    context = {
        'evento': evento,
        'registros': registros,
        'form_inscripcion': form_inscripcion,
    }
    return render(request, 'eventos/evento_detalle.html', context)


def evento_crear(request):
    """Creación de un nuevo evento"""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            nuevo_evento = form.save()
            messages.success(request, f"Evento '{nuevo_evento.titulo}' creado exitosamente.")
            return redirect('evento_detalle', pk=nuevo_evento.pk)
    else:
        form = EventoForm()
    return render(request, 'eventos/evento_form.html', {'form': form, 'accion': 'Crear Evento'})


def evento_editar(request, pk):
    """Edición de información de un evento"""
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, f"Evento '{evento.titulo}' actualizado exitosamente.")
            return redirect('evento_detalle', pk=evento.pk)
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/evento_form.html', {'form': form, 'evento': evento, 'accion': 'Editar Evento'})


def evento_eliminar(request, pk):
    """Eliminación de un evento"""
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        titulo = evento.titulo
        evento.delete()
        messages.success(request, f"Evento '{titulo}' y sus registros asociados fueron eliminados correctamente.")
        return redirect('evento_lista')
    return render(request, 'eventos/evento_confirm_delete.html', {'evento': evento})


# ==========================================
# CRUD DE USUARIOS
# ==========================================

def usuario_lista(request):
    """Lista de usuarios con estadísticas anotadas mediante Django ORM"""
    usuarios = Usuario.objects.annotate(
        total_org=Count('eventos_organizados', distinct=True),
        total_reg=Count('registros', distinct=True)
    ).order_by('nombre')

    context = {
        'usuarios': usuarios,
    }
    return render(request, 'eventos/usuario_lista.html', context)


def usuario_crear(request):
    """Creación de un usuario"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f"Usuario '{usuario.nombre}' registrado con éxito.")
            return redirect('usuario_lista')
    else:
        form = UsuarioForm()
    return render(request, 'eventos/usuario_form.html', {'form': form, 'accion': 'Crear Usuario'})


def usuario_editar(request, pk):
    """Edición de usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{usuario.nombre}' actualizado correctamente.")
            return redirect('usuario_lista')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'eventos/usuario_form.html', {'form': form, 'usuario': usuario, 'accion': 'Editar Usuario'})


def usuario_eliminar(request, pk):
    """Eliminación de usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        nombre = usuario.nombre
        usuario.delete()
        messages.success(request, f"Usuario '{nombre}' eliminado.")
        return redirect('usuario_lista')
    return render(request, 'eventos/usuario_confirm_delete.html', {'usuario': usuario})


# ==========================================
# CRUD DE REGISTROS A EVENTOS
# ==========================================

def registro_lista(request):
    """Lista y administración de todos los registros a eventos"""
    registros = RegistroEvento.objects.select_related('evento', 'usuario').all()
    estado = request.GET.get('estado')
    if estado:
        registros = registros.filter(estado=estado)

    context = {
        'registros': registros,
        'estado_filtro': estado,
    }
    return render(request, 'eventos/registro_lista.html', context)


def registro_crear(request):
    """Registrar un usuario en un evento mediante formulario completo"""
    if request.method == 'POST':
        form = RegistroEventoForm(request.POST)
        if form.is_valid():
            reg = form.save()
            messages.success(request, f"Registro creado: {reg.usuario.nombre} inscrito en {reg.evento.titulo}.")
            return redirect('registro_lista')
    else:
        form = RegistroEventoForm()
    return render(request, 'eventos/registro_form.html', {'form': form, 'accion': 'Registrar Participación'})


def registro_eliminar(request, pk):
    """Cancelar / Eliminar un registro de evento"""
    registro = get_object_or_404(RegistroEvento, pk=pk)
    evento_id = registro.evento.id
    if request.method == 'POST':
        usuario_nom = registro.usuario.nombre
        evento_tit = registro.evento.titulo
        registro.delete()
        messages.success(request, f"Inscripción de '{usuario_nom}' en '{evento_tit}' cancelada.")
        return redirect('evento_detalle', pk=evento_id)
    return render(request, 'eventos/registro_confirm_delete.html', {'registro': registro})


# ==========================================
# PANEL DE CONSULTAS AVANZADAS DJANGO ORM
# (Cumplimiento estricto de la Rúbrica)
# ==========================================

def consultas_avanzadas(request):
    """
    Vista dedicada que ejecuta y muestra de forma interactiva las 5 consultas
    avanzadas solicitadas en la rúbrica del laboratorio, con código ORM visible.
    """
    ahora = timezone.now()

    # 1. ¿Cuántos usuarios están registrados en un evento específico?
    # Usando annotate y Count()
    eventos_con_conteo = Evento.objects.annotate(
        total_usuarios=Count('registros')
    ).select_related('organizador').order_by('-total_usuarios')

    evento_seleccionado_id = request.GET.get('evento_id', '').strip()
    evento_seleccionado = None
    if evento_seleccionado_id.isdigit():
        evento_seleccionado = Evento.objects.filter(pk=int(evento_seleccionado_id)).annotate(
            total_usuarios=Count('registros')
        ).first()

    # 2. ¿Cuántos eventos se están llevando a cabo este mes?
    # Usando filter con lookups temporales __year y __month
    eventos_este_mes = Evento.objects.filter(
        fecha__year=ahora.year,
        fecha__month=ahora.month
    ).order_by('fecha')
    total_eventos_este_mes = eventos_este_mes.count()

    # 3. ¿Quiénes son los usuarios más activos en términos de participación en eventos?
    # Usando annotate(Count()) y order_by('-total')
    usuarios_mas_activos = Usuario.objects.annotate(
        total_participaciones=Count('registros')
    ).order_by('-total_participaciones')[:5]

    # 4. ¿Cuántos eventos ha organizado un usuario en particular?
    # Usando annotate(Count('eventos_organizados'))
    usuarios_organizadores = Usuario.objects.annotate(
        total_organizados=Count('eventos_organizados')
    ).filter(total_organizados__gt=0).order_by('-total_organizados')

    # 5. Consulta compleja con Q Objects (Múltiples condiciones OR / AND / NOT)
    # Ejemplo: Eventos con capacidad >= 50 O que contengan "Tecsup" o "Python" en título/descripción
    q_query = request.GET.get('q_busqueda', 'Tecsup')
    consulta_q = Evento.objects.filter(
        (Q(titulo__icontains=q_query) | Q(descripcion__icontains=q_query)) &
        Q(capacidad__gte=30)
    ).distinct()

    # 6. Agregaciones estadísticas globales con aggregate()
    estadisticas = Evento.objects.aggregate(
        total_eventos=Count('id'),
        promedio_capacidad=Avg('capacidad'),
        max_capacidad=Max('capacidad'),
        min_capacidad=Min('capacidad'),
        capacidad_total_combinada=Sum('capacidad')
    )

    context = {
        'ahora': ahora,
        'eventos_con_conteo': eventos_con_conteo,
        'evento_seleccionado': evento_seleccionado,
        'eventos_este_mes': eventos_este_mes,
        'total_eventos_este_mes': total_eventos_este_mes,
        'usuarios_mas_activos': usuarios_mas_activos,
        'usuarios_organizadores': usuarios_organizadores,
        'consulta_q': consulta_q,
        'q_query': q_query,
        'estadisticas': estadisticas,
    }
    return render(request, 'eventos/consultas_avanzadas.html', context)
