# Sistema de Gestion de Eventos - Laboratorio 07 (Django ORM)

Proyecto Django orientado a la implementacion de modelos relacionales, operaciones CRUD y consultas avanzadas mediante Django ORM (`filter`, `exclude`, `get`, `Q`, `annotate`, `aggregate`, `select_related` y `prefetch_related`).

**Curso:** Desarrollo de Aplicaciones Empresariales  
**Institucion:** TECSUP - Diseno y Desarrollo de Software (Ciclo IV)  
**Estudiante:** Omar Steve Campos Noriega  
**Docente:** Hector Manrique Morante  

---

## Estructura del Repositorio

```text
semana7/
|-- ejecutar_consultas_orm.py     # Script de verificacion de consultas ORM en consola
|-- iniciar_proyecto.bat          # Script de arranque para Windows
|-- requirements.txt              # Dependencias del proyecto
|-- README.md
`-- lab07/                        # Proyecto Django
    |-- manage.py
    |-- poblar_datos.py           # Seed idempotente de datos iniciales
    |-- lab07/                    # Configuracion central (settings, urls, wsgi, asgi)
    |-- eventos/                  # Caso de estudio: Usuario, Evento, RegistroEvento
    |-- recetas/                  # Ejercicio guiado: Autor, Receta, Comentario
    `-- templates/                # Plantillas HTML con Bootstrap 5
```

---

## Modelos Implementados

### Aplicacion `eventos`
- `Usuario`: `nombre`, `email` (unico), `telefono`, `ciudad`, `fecha_registro`.
- `Evento`: `titulo`, `descripcion`, `fecha`, `ubicacion`, `capacidad`, `organizador` (`ForeignKey` a `Usuario`), `creado_en`. Propiedades calculadas: `total_inscritos`, `cupos_disponibles`, `es_este_mes`.
- `RegistroEvento`: relacion intermedia entre `Evento` y `Usuario` con `estado` (`CONFIRMADO`, `PENDIENTE`, `CANCELADO`), `observaciones`, `fecha_registro` y restriccion `unique_together = ('evento', 'usuario')`.

### Aplicacion `recetas`
- `Autor`: `nombre`, `email`.
- `Receta`: `titulo` (unico), `ingredientes`, `preparacion`, `tiempo_registro`, `autor` (`ForeignKey` a `Autor`).
- `Comentario`: `receta` (`ForeignKey` a `Receta`), `texto`.

---

## Consultas ORM Cubiertas

| Caso | Implementacion ORM | Ubicacion |
| :--- | :--- | :--- |
| Inscritos por evento | `Evento.objects.annotate(total_usuarios=Count('registros'))` | `eventos/views.py` |
| Eventos del mes actual | `Evento.objects.filter(fecha__year=..., fecha__month=...)` | `eventos/views.py` |
| Usuarios mas activos | `Usuario.objects.annotate(total_participaciones=Count('registros')).order_by('-total_participaciones')[:5]` | `eventos/views.py` |
| Eventos por organizador | `Usuario.objects.annotate(total_organizados=Count('eventos_organizados')).filter(total_organizados__gt=0)` | `eventos/views.py` |
| Busqueda multicriterio | `Evento.objects.filter((Q(titulo__icontains=q) \| Q(descripcion__icontains=q)) & Q(capacidad__gte=30))` | `eventos/views.py` |
| Estadisticas globales | `Evento.objects.aggregate(Count('id'), Avg('capacidad'), Max('capacidad'), Min('capacidad'), Sum('capacidad'))` | `eventos/views.py` |
| Filtros de recetas | `exclude(ingredientes__startswith='A')`, `filter(preparacion__contains='tetera')`, `order_by('titulo')` | `recetas/views.py` |

---

## Instalacion y Ejecucion Local

### 1. Entorno virtual y dependencias

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Migraciones y datos iniciales

```powershell
cd lab07
python manage.py migrate
python poblar_datos.py
```

Credenciales de administracion generadas por `poblar_datos.py`:
- **Usuario:** `admin`
- **Contrasena:** `Tecsup2019`

### 3. Servidor de desarrollo

```powershell
python manage.py runserver 127.0.0.1:8000
```

En Windows tambien se puede ejecutar `iniciar_proyecto.bat` desde la raiz del repositorio.

### 4. Verificacion de consultas ORM por consola

```powershell
.\venv\Scripts\python.exe ejecutar_consultas_orm.py
```

### 5. Pruebas automatizadas

```powershell
cd lab07
..\venv\Scripts\python.exe manage.py test
```

---

## Rutas Principales

- `/` — Panel resumen con metricas KPI y proximos eventos.
- `/consultas-avanzadas/` — Ejecucion y detalle de consultas ORM solicitadas.
- `/eventos/` — Listado, busqueda con `Q` objects y CRUD de eventos.
- `/usuarios/` — Directorio y CRUD de usuarios con conteos anotados.
- `/registros/` — Gestion de inscripciones y validacion de aforo.
- `/recetas/` — Vista de modelos y filtros de la aplicacion `recetas`.
- `/admin/` — Panel administrativo de Django.
