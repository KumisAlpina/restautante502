from decimal import Decimal

from django import forms
from django.contrib.auth.models import Group, User
from django.forms import inlineformset_factory

from .models import Cliente, DetalleOrden, Empleado, Factura, Mesa, Orden, Plato

IVA_RATE = Decimal('0.12')


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'correo']
        labels = {
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'correo': 'Correo',
        }


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'cargo', 'telefono', 'correo']
        labels = {
            'nombre': 'Nombre',
            'cargo': 'Cargo',
            'telefono': 'Teléfono',
            'correo': 'Correo',
        }
        widgets = {
            'cargo': forms.Select(),
        }


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero_mesa', 'capacidad', 'estado_mesa']
        labels = {
            'numero_mesa': 'Número de mesa',
            'capacidad': 'Capacidad',
            'estado_mesa': 'Estado',
        }
        widgets = {
            'numero_mesa': forms.NumberInput(attrs={'min': 1}),
            'capacidad': forms.NumberInput(attrs={'min': 1}),
            'estado_mesa': forms.Select(),
        }


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre_plato', 'descripcion', 'precio', 'categoria', 'disponible']
        labels = {
            'nombre_plato': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'categoria': 'Categoría',
            'disponible': 'Disponible',
        }
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'disponible': forms.CheckboxInput(),
        }


class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['cliente', 'empleado', 'mesa', 'estado_orden']
        labels = {
            'cliente': 'Cliente',
            'empleado': 'Empleado',
            'mesa': 'Mesa',
            'estado_orden': 'Estado',
        }
        widgets = {
            'estado_orden': forms.Select(),
        }


class DetalleOrdenForm(forms.ModelForm):
    class Meta:
        model = DetalleOrden
        fields = ['plato', 'cantidad']
        labels = {
            'plato': 'Plato',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 1, 'class': 'input-cantidad'}),
            'plato': forms.Select(attrs={'class': 'select-plato'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plato'].queryset = Plato.objects.filter(disponible=True).order_by('nombre_plato')
        self.fields['plato'].label_from_instance = (
            lambda obj: f'{obj.nombre_plato} — Q{obj.precio}'
        )


class BaseDetalleOrdenFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        lineas = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        if not lineas:
            raise forms.ValidationError('Agregue al menos un plato a la orden.')


DetalleOrdenFormSet = inlineformset_factory(
    Orden,
    DetalleOrden,
    form=DetalleOrdenForm,
    formset=BaseDetalleOrdenFormSet,
    extra=2,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['orden', 'subtotal', 'impuesto', 'total_factura', 'metodo_pago']
        labels = {
            'orden': 'Orden',
            'subtotal': 'Subtotal',
            'impuesto': 'Impuesto',
            'total_factura': 'Total factura',
            'metodo_pago': 'Método de pago',
        }
        widgets = {
            'subtotal': forms.NumberInput(attrs={'step': '0.01'}),
            'impuesto': forms.NumberInput(attrs={'step': '0.01'}),
            'total_factura': forms.NumberInput(attrs={'step': '0.01'}),
            'metodo_pago': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Factura.objects.all()
        if self.instance.pk:
            ocupados = qs.exclude(pk=self.instance.pk).values_list('orden_id', flat=True)
        else:
            ocupados = qs.values_list('orden_id', flat=True)
        self.fields['orden'].queryset = (
            Orden.objects.exclude(id__in=ocupados)
            .exclude(estado_orden='Cancelada')
            .exclude(estado_orden='Facturada')
            .prefetch_related('detalles__plato')
        )
        self.fields['orden'].label_from_instance = (
            lambda obj: f'Orden #{obj.id} — Mesa {obj.mesa.numero_mesa} — Q{obj.total}'
        )
        self._aplicar_totales_desde_orden()

    def _orden_seleccionada(self):
        if self.data.get('orden'):
            return Orden.objects.filter(pk=self.data.get('orden')).prefetch_related('detalles__plato').first()
        if self.initial.get('orden'):
            pk = self.initial['orden']
            if hasattr(pk, 'pk'):
                pk = pk.pk
            return Orden.objects.filter(pk=pk).prefetch_related('detalles__plato').first()
        if self.instance.pk and self.instance.orden_id:
            return self.instance.orden
        return None

    def _aplicar_totales_desde_orden(self):
        orden = self._orden_seleccionada()
        if not orden:
            return
        subtotal = orden.total or Decimal('0.00')
        impuesto = (subtotal * IVA_RATE).quantize(Decimal('0.01'))
        total = subtotal + impuesto
        self.fields['subtotal'].initial = subtotal
        if not self.instance.pk:
            self.fields['impuesto'].initial = impuesto
            self.fields['total_factura'].initial = total
        self.fields['subtotal'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned = super().clean()
        orden = cleaned.get('orden')
        if orden:
            if not orden.detalles.exists():
                self.add_error('orden', 'La orden no tiene platos registrados.')
            elif (orden.total or Decimal('0')) <= 0:
                self.add_error('orden', 'El total de la orden debe ser mayor a cero.')
            subtotal = orden.total or Decimal('0.00')
            cleaned['subtotal'] = subtotal
            impuesto = cleaned.get('impuesto')
            if impuesto is None:
                impuesto = (subtotal * IVA_RATE).quantize(Decimal('0.01'))
                cleaned['impuesto'] = impuesto
            total = cleaned.get('total_factura')
            if total is None:
                cleaned['total_factura'] = subtotal + impuesto
        return cleaned

    def save(self, commit=True):
        factura = super().save(commit=commit)
        if commit:
            orden = factura.orden
            orden.estado_orden = 'Facturada'
            orden.save(update_fields=['estado_orden'])
            mesa = orden.mesa
            mesa.estado_mesa = 'Disponible'
            mesa.save(update_fields=['estado_mesa'])
        return factura


SYSTEM_ROLES = ('Administrador', 'Mesero', 'Cajero')


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label='Contraseña',
        widget=forms.PasswordInput(render_value=False),
        help_text='Déjalo vacío para mantener la contraseña actual.',
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__in=SYSTEM_ROLES),
        required=True,
        empty_label=None,
        label='Grupo',
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Usuario',
            'email': 'Correo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            current = self.instance.groups.filter(name__in=SYSTEM_ROLES).first()
            if current:
                self.fields['grupo'].initial = current
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Contraseña obligatoria al crear el usuario.'

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get('password') or ''
        if raw_password:
            user.set_password(raw_password)
        if commit:
            user.save()
            group = self.cleaned_data['grupo']
            user.groups.set([group])
        return user
