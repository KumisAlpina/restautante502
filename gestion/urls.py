# gestion/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    # Cliente
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    # Empleado
    path('empleados/crear/', views.empleado_crear, name='empleado_crear'),
    path('empleados/<int:pk>/editar/', views.empleado_editar, name='empleado_editar'),
    path('empleados/<int:pk>/eliminar/', views.empleado_eliminar, name='empleado_eliminar'),
    path('empleados/', views.empleado_lista, name='empleado_lista'),
    # Mesa
    path('mesas/crear/', views.mesa_crear, name='mesa_crear'),
    path('mesas/<int:pk>/editar/', views.mesa_editar, name='mesa_editar'),
    path('mesas/<int:pk>/eliminar/', views.mesa_eliminar, name='mesa_eliminar'),
    path('mesas/', views.mesa_lista, name='mesa_lista'),
    # Plato
    path('platos/crear/', views.plato_crear, name='plato_crear'),
    path('platos/<int:pk>/editar/', views.plato_editar, name='plato_editar'),
    path('platos/<int:pk>/eliminar/', views.plato_eliminar, name='plato_eliminar'),
    path('platos/', views.plato_lista, name='plato_lista'),
    # Orden
    path('ordenes/crear/', views.orden_crear, name='orden_crear'),
    path('ordenes/<int:pk>/editar/', views.orden_editar, name='orden_editar'),
    path('ordenes/<int:pk>/eliminar/', views.orden_eliminar, name='orden_eliminar'),
    path('ordenes/', views.orden_lista, name='orden_lista'),
    # Factura
    path('facturas/crear/', views.factura_crear, name='factura_crear'),
    path('facturas/<int:pk>/editar/', views.factura_editar, name='factura_editar'),
    path('facturas/<int:pk>/eliminar/', views.factura_eliminar, name='factura_eliminar'),
    path('facturas/', views.factura_lista, name='factura_lista'),
]
