from django import forms

from .models import Cliente, Empleado, Mesa, Plato, Orden, Factura


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
        fields = ['cliente', 'empleado', 'mesa', 'estado_orden', 'total']
        labels = {
            'cliente': 'Cliente',
            'empleado': 'Empleado',
            'mesa': 'Mesa',
            'estado_orden': 'Estado',
            'total': 'Total',
        }
        widgets = {
            'estado_orden': forms.Select(),
            'total': forms.NumberInput(attrs={'step': '0.01'}),
        }


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
        self.fields['orden'].queryset = Orden.objects.exclude(id__in=ocupados)
