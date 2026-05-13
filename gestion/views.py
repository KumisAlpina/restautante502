# gestion/views.py
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ClienteForm,
    EmpleadoForm,
    FacturaForm,
    MesaForm,
    OrdenForm,
    PlatoForm,
)
from .models import Cliente, Empleado, Factura, Mesa, Orden, Plato


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos de administrador')
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)

    return _wrapped


@admin_required
def inicio(request):
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_empleados': Empleado.objects.count(),
        'total_mesas': Mesa.objects.count(),
        'total_platos': Plato.objects.count(),
        'total_ordenes': Orden.objects.count(),
        'total_facturas': Factura.objects.count(),
    }
    return render(request, 'gestion/inicio.html', context)


# --- Cliente ---
@admin_required
def cliente_lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'gestion/cliente_lista.html', {'clientes': clientes})


@admin_required
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    return render(request, 'gestion/cliente_form.html', {'form': form, 'titulo': 'Crear cliente'})


@admin_required
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


@admin_required
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('cliente_lista')
    return render(request, 'gestion/cliente_confirm_delete.html', {'cliente': cliente})


# --- Empleado ---
@admin_required
def empleado_lista(request):
    empleados = Empleado.objects.all()
    return render(request, 'gestion/empleado_lista.html', {'empleados': empleados})


@admin_required
def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empleado_lista')
    else:
        form = EmpleadoForm()
    return render(request, 'gestion/empleado_form.html', {'form': form, 'titulo': 'Crear empleado'})


@admin_required
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


@admin_required
def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('empleado_lista')
    return render(request, 'gestion/empleado_confirm_delete.html', {'empleado': empleado})


# --- Mesa ---
@admin_required
def mesa_lista(request):
    mesas = Mesa.objects.all()
    return render(request, 'gestion/mesa_lista.html', {'mesas': mesas})


@admin_required
def mesa_crear(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mesa_lista')
    else:
        form = MesaForm()
    return render(request, 'gestion/mesa_form.html', {'form': form, 'titulo': 'Crear mesa'})


@admin_required
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


@admin_required
def mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        return redirect('mesa_lista')
    return render(request, 'gestion/mesa_confirm_delete.html', {'mesa': mesa})


# --- Plato ---
@admin_required
def plato_lista(request):
    platos = Plato.objects.all()
    return render(request, 'gestion/plato_lista.html', {'platos': platos})


@admin_required
def plato_crear(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plato_lista')
    else:
        form = PlatoForm()
    return render(request, 'gestion/plato_form.html', {'form': form, 'titulo': 'Crear plato'})


@admin_required
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


@admin_required
def plato_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        return redirect('plato_lista')
    return render(request, 'gestion/plato_confirm_delete.html', {'plato': plato})


# --- Orden ---
@admin_required
def orden_lista(request):
    ordenes = Orden.objects.select_related('cliente', 'empleado', 'mesa').all()
    return render(request, 'gestion/orden_lista.html', {'ordenes': ordenes})


@admin_required
def orden_crear(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('orden_lista')
    else:
        form = OrdenForm()
    return render(request, 'gestion/orden_form.html', {'form': form, 'titulo': 'Crear orden'})


@admin_required
def orden_editar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            return redirect('orden_lista')
    else:
        form = OrdenForm(instance=orden)
    return render(
        request,
        'gestion/orden_form.html',
        {'form': form, 'titulo': 'Editar orden', 'orden': orden},
    )


@admin_required
def orden_eliminar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        orden.delete()
        return redirect('orden_lista')
    return render(request, 'gestion/orden_confirm_delete.html', {'orden': orden})


# --- Factura ---
@admin_required
def factura_lista(request):
    facturas = Factura.objects.select_related('orden').all()
    return render(request, 'gestion/factura_lista.html', {'facturas': facturas})


@admin_required
def factura_crear(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('factura_lista')
    else:
        form = FacturaForm()
    return render(request, 'gestion/factura_form.html', {'form': form, 'titulo': 'Crear factura'})


@admin_required
def factura_editar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
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
        {'form': form, 'titulo': 'Editar factura', 'factura': factura},
    )


@admin_required
def factura_eliminar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.delete()
        return redirect('factura_lista')
    return render(request, 'gestion/factura_confirm_delete.html', {'factura': factura})


class LoginView(AuthLoginView):
    template_name = 'gestion/login.html'


class LogoutView(AuthLogoutView):
    next_page = '/login/'
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)
