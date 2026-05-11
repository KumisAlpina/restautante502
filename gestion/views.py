# gestion/views.py
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import Cliente, Empleado, Mesa, Plato, Orden, Factura


class AdminRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos de administrador')
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class InicioView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clientes'] = Cliente.objects.count()
        context['total_empleados'] = Empleado.objects.count()
        context['total_mesas'] = Mesa.objects.count()
        context['total_platos'] = Plato.objects.count()
        context['total_ordenes'] = Orden.objects.count()
        context['total_facturas'] = Factura.objects.count()
        return context


class ListaClientesView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/clientes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        return context


class ListaEmpleadosView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/empleados.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empleados'] = Empleado.objects.all()
        return context


class ListaMesasView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/mesas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mesas'] = Mesa.objects.all()
        return context


class ListaPlatosView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/platos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platos'] = Plato.objects.all()
        return context


class ListaOrdenesView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/ordenes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordenes'] = Orden.objects.all()
        return context


class ListaFacturasView(AdminRequiredMixin, TemplateView):
    template_name = 'gestion/facturas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facturas'] = Factura.objects.all()
        return context


class LoginView(AuthLoginView):
    template_name = 'gestion/login.html'


class LogoutView(AuthLogoutView):
    next_page = '/login/'
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)
