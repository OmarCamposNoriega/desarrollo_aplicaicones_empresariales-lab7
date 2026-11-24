from django import forms
from .models import Evento, Usuario, RegistroEvento


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha', 'ubicacion', 'capacidad', 'organizador']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Conferencia Internacional de Inteligencia Artificial'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe los temas, agenda y detalles...'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Auditorio Tecsup / Virtual Zoom'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Ej. 100'}),
            'organizador': forms.Select(attrs={'class': 'form-select'}),
        }


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'ciudad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@tecsup.edu.pe'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+51 987 654 321'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lima'}),
        }


class RegistroEventoForm(forms.ModelForm):
    class Meta:
        model = RegistroEvento
        fields = ['evento', 'usuario', 'estado', 'observaciones']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional (Ej. Requerimientos especiales)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        evento = cleaned_data.get('evento')
        usuario = cleaned_data.get('usuario')
        estado = cleaned_data.get('estado')

        if evento and usuario:
            # Check duplicate if new record
            existente = RegistroEvento.objects.filter(evento=evento, usuario=usuario)
            if self.instance.pk:
                existente = existente.exclude(pk=self.instance.pk)
            if existente.exists():
                raise forms.ValidationError(f"El usuario '{usuario.nombre}' ya se encuentra registrado en el evento '{evento.titulo}'.")

            if estado == 'CONFIRMADO' and evento.cupos_disponibles <= 0 and not (self.instance.pk and self.instance.estado == 'CONFIRMADO'):
                raise forms.ValidationError(f"El evento '{evento.titulo}' ha alcanzado su capacidad máxima ({evento.capacidad} participantes).")

        return cleaned_data


class InscripcionDirectaForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Selecciona un Usuario --"
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observaciones (opcional)'})
    )

