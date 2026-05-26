# gestion/views.py
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from decimal import Decimal

from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ClienteForm,
    DetalleOrdenFormSet,
    EmpleadoForm,
    FacturaForm,
    IVA_RATE,
    MesaForm,
    OrdenForm,
    PlatoForm,
    UsuarioForm,
)
from .models import Cliente, Empleado, Factura, Mesa, Orden, Plato
from .permissions import user_is_solo_cajero, user_is_solo_mesero


def _marcar_mesa_ocupada(orden):
    mesa = orden.mesa
    if mesa.estado_mesa != 'Ocupada' and orden.estado_orden not in ('Facturada', 'Cancelada'):
        mesa.estado_mesa = 'Ocupada'
        mesa.save(update_fields=['estado_mesa'])


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if roles and not request.user.groups.filter(name__in=roles).exists():
                messages.error(request, 'No tienes permisos para acceder a esta sección')
                return redirect('/sin-permiso/')

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


@role_required('Administrador', 'Mesero', 'Cajero')
def inicio(request):
    total_platos = Plato.objects.count()
    if user_is_solo_mesero(request.user):
        total_platos = Plato.objects.filter(disponible=True).count()

    total_ordenes = Orden.objects.count()
    if user_is_solo_cajero(request.user):
        total_ordenes = (
            Orden.objects.filter(factura__isnull=True).exclude(estado_orden='Cancelada').count()
        )

    context = {
        'total_clientes': Cliente.objects.count(),
        'total_empleados': Empleado.objects.count(),
        'total_mesas': Mesa.objects.count(),
        'total_platos': total_platos,
        'total_ordenes': total_ordenes,
        'total_facturas': Factura.objects.count(),
    }
    return render(request, 'gestion/inicio.html', context)

@role_required('Administrador', 'Mesero', 'Cajero')
def sin_permiso(request):
    return render(request, 'gestion/sin_permiso.html')


# --- Cliente ---
@role_required('Administrador', 'Mesero')
def cliente_lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'gestion/cliente_lista.html', {'clientes': clientes})


@role_required('Administrador')
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    return render(request, 'gestion/cliente_form.html', {'form': form, 'titulo': 'Crear cliente'})


@role_required('Administrador')
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(
        request,
        'gestion/cliente_form.html',
        {'form': form, 'titulo': 'Editar cliente', 'cliente': cliente},
    )


@role_required('Administrador')
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('cliente_lista')
    return render(request, 'gestion/cliente_confirm_delete.html', {'cliente': cliente})


# --- Empleado ---
@role_required('Administrador')
def empleado_lista(request):
    empleados = Empleado.objects.all()
    return render(request, 'gestion/empleado_lista.html', {'empleados': empleados})


@role_required('Administrador')
def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empleado_lista')
    else:
        form = EmpleadoForm()
    return render(request, 'gestion/empleado_form.html', {'form': form, 'titulo': 'Crear empleado'})


@role_required('Administrador')
def empleado_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleado_lista')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(
        request,
        'gestion/empleado_form.html',
        {'form': form, 'titulo': 'Editar empleado', 'empleado': empleado},
    )


@role_required('Administrador')
def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('empleado_lista')
    return render(request, 'gestion/empleado_confirm_delete.html', {'empleado': empleado})


# --- Mesa ---
@role_required('Administrador', 'Mesero')
def mesa_lista(request):
    mesas = Mesa.objects.all()
    return render(request, 'gestion/mesa_lista.html', {'mesas': mesas})


@role_required('Administrador')
def mesa_crear(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mesa_lista')
    else:
        form = MesaForm()
    return render(request, 'gestion/mesa_form.html', {'form': form, 'titulo': 'Crear mesa'})


@role_required('Administrador')
def mesa_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            return redirect('mesa_lista')
    else:
        form = MesaForm(instance=mesa)
    return render(
        request,
        'gestion/mesa_form.html',
        {'form': form, 'titulo': 'Editar mesa', 'mesa': mesa},
    )


@role_required('Administrador')
def mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        return redirect('mesa_lista')
    return render(request, 'gestion/mesa_confirm_delete.html', {'mesa': mesa})


# --- Plato ---
@role_required('Administrador', 'Mesero')
def plato_lista(request):
    platos = Plato.objects.all()
    if user_is_solo_mesero(request.user):
        platos = platos.filter(disponible=True)
    titulo = 'Menú disponible' if user_is_solo_mesero(request.user) else 'Platos'
    return render(request, 'gestion/plato_lista.html', {'platos': platos, 'titulo': titulo})


@role_required('Administrador')
def plato_crear(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plato_lista')
    else:
        form = PlatoForm()
    return render(request, 'gestion/plato_form.html', {'form': form, 'titulo': 'Crear plato'})


@role_required('Administrador')
def plato_editar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            return redirect('plato_lista')
    else:
        form = PlatoForm(instance=plato)
    return render(
        request,
        'gestion/plato_form.html',
        {'form': form, 'titulo': 'Editar plato', 'plato': plato},
    )


@role_required('Administrador')
def plato_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        return redirect('plato_lista')
    return render(request, 'gestion/plato_confirm_delete.html', {'plato': plato})


# --- Orden ---
@role_required('Administrador', 'Mesero', 'Cajero')
def orden_lista(request):
    ordenes = (
        Orden.objects.select_related('cliente', 'empleado', 'mesa')
        .prefetch_related('detalles__plato')
        .annotate(tiene_factura=Exists(Factura.objects.filter(orden_id=OuterRef('pk'))))
    )
    titulo = 'Órdenes'
    if user_is_solo_cajero(request.user):
        ordenes = ordenes.filter(tiene_factura=False).exclude(estado_orden='Cancelada')
        titulo = 'Órdenes pendientes de pago'
    return render(request, 'gestion/orden_lista.html', {'ordenes': ordenes, 'titulo': titulo})


@role_required('Administrador', 'Mesero')
def orden_crear(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        formset = DetalleOrdenFormSet(request.POST)
        if form.is_valid():
            orden = form.save()
            formset = DetalleOrdenFormSet(request.POST, instance=orden)
            if formset.is_valid():
                formset.save()
                orden.recalcular_total()
                _marcar_mesa_ocupada(orden)
                messages.success(
                    request,
                    f'Orden #{orden.id} registrada con {orden.detalles.count()} plato(s).',
                )
                return redirect('orden_lista')
            orden.delete()
    else:
        form = OrdenForm()
        formset = DetalleOrdenFormSet()
    return render(
        request,
        'gestion/orden_form.html',
        {'form': form, 'formset': formset, 'titulo': 'Crear orden'},
    )


@role_required('Administrador', 'Mesero')
def orden_editar(request, pk):
    orden = get_object_or_404(Orden.objects.prefetch_related('detalles__plato'), pk=pk)
    if request.method == 'POST':
        form = OrdenForm(request.POST, instance=orden)
        formset = DetalleOrdenFormSet(request.POST, instance=orden)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            formset.save()
            orden.recalcular_total()
            _marcar_mesa_ocupada(orden)
            messages.success(request, f'Orden #{orden.id} actualizada.')
            return redirect('orden_lista')
    else:
        form = OrdenForm(instance=orden)
        formset = DetalleOrdenFormSet(instance=orden)
    return render(
        request,
        'gestion/orden_form.html',
        {
            'form': form,
            'formset': formset,
            'titulo': 'Editar orden',
            'orden': orden,
            'total_orden': orden.total,
        },
    )


@role_required('Administrador', 'Mesero', 'Cajero')
def orden_resumen(request, pk):
    orden = get_object_or_404(Orden.objects.prefetch_related('detalles__plato'), pk=pk)
    subtotal = orden.total or Decimal('0.00')
    impuesto = (subtotal * IVA_RATE).quantize(Decimal('0.01'))
    return JsonResponse({
        'id': orden.id,
        'mesa': orden.mesa.numero_mesa,
        'cliente': orden.cliente.nombre,
        'subtotal': str(subtotal),
        'impuesto': str(impuesto),
        'total': str(subtotal + impuesto),
        'detalles': [
            {
                'plato': d.plato.nombre_plato,
                'cantidad': d.cantidad,
                'precio_unitario': str(d.precio_unitario),
                'subtotal': str(d.subtotal),
            }
            for d in orden.detalles.all()
        ],
    })


@role_required('Administrador')
def orden_eliminar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        orden.delete()
        return redirect('orden_lista')
    return render(request, 'gestion/orden_confirm_delete.html', {'orden': orden})


# --- Factura ---
@role_required('Administrador', 'Cajero')
def factura_lista(request):
    facturas = (
        Factura.objects.select_related('orden', 'orden__mesa', 'orden__cliente')
        .prefetch_related('orden__detalles__plato')
    )
    return render(request, 'gestion/factura_lista.html', {'facturas': facturas})


def _orden_para_factura(request, form):
    orden_id = request.GET.get('orden') or request.POST.get('orden')
    if orden_id:
        return Orden.objects.filter(pk=orden_id).prefetch_related('detalles__plato').first()
    if form.instance.pk and form.instance.orden_id:
        return form.instance.orden
    return form._orden_seleccionada()


@role_required('Administrador', 'Cajero')
def factura_crear(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura registrada y cuenta cerrada correctamente.')
            return redirect('factura_lista')
    else:
        initial = {}
        orden_id = request.GET.get('orden')
        if orden_id:
            initial['orden'] = orden_id
        form = FacturaForm(initial=initial)
    orden_preview = _orden_para_factura(request, form)
    return render(
        request,
        'gestion/factura_form.html',
        {
            'form': form,
            'titulo': 'Crear factura',
            'orden_preview': orden_preview,
            'iva_rate': IVA_RATE,
        },
    )


@role_required('Administrador', 'Cajero')
def factura_editar(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related('orden').prefetch_related('orden__detalles__plato'),
        pk=pk,
    )
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            return redirect('factura_lista')
    else:
        form = FacturaForm(instance=factura)
    return render(
        request,
        'gestion/factura_form.html',
        {
            'form': form,
            'titulo': 'Editar factura',
            'factura': factura,
            'orden_preview': factura.orden,
            'iva_rate': IVA_RATE,
        },
    )


@role_required('Administrador')
def factura_eliminar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.delete()
        return redirect('factura_lista')
    return render(request, 'gestion/factura_confirm_delete.html', {'factura': factura})

@role_required('Administrador')
def usuario_lista(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'gestion/usuario_lista.html', {'usuarios': usuarios})


@role_required('Administrador')
def usuario_crear(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" creado correctamente')
            return redirect('usuario_lista')
    else:
        form = UsuarioForm()
    return render(request, 'gestion/usuario_form.html', {'form': form, 'titulo': 'Crear usuario'})


@role_required('Administrador')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" actualizado correctamente')
            return redirect('usuario_lista')
    else:
        form = UsuarioForm(instance=usuario)
    return render(
        request,
        'gestion/usuario_form.html',
        {'form': form, 'titulo': 'Editar usuario', 'usuario': usuario},
    )


@role_required('Administrador')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado correctamente')
        return redirect('usuario_lista')
    return render(request, 'gestion/usuario_confirm_delete.html', {'usuario': usuario})


class LoginView(AuthLoginView):
    template_name = 'gestion/login.html'


class LogoutView(AuthLogoutView):
    next_page = '/login/'
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)
