# gestion/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('clientes/', views.ListaClientesView.as_view(), name='lista_clientes'),
    path('empleados/', views.ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('mesas/', views.ListaMesasView.as_view(), name='lista_mesas'),
    path('platos/', views.ListaPlatosView.as_view(), name='lista_platos'),
    path('ordenes/', views.ListaOrdenesView.as_view(), name='lista_ordenes'),
    path('facturas/', views.ListaFacturasView.as_view(), name='lista_facturas'),
]
