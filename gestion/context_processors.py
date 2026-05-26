from .permissions import user_roles


def permisos_nav(request):
    roles = user_roles(request.user)
    admin = 'Administrador' in roles
    mesero = 'Mesero' in roles
    cajero = 'Cajero' in roles
    user = request.user

    return {
        'rol_admin': admin,
        'rol_mesero': mesero,
        'rol_cajero': cajero,
        'nav_inicio': admin or mesero or cajero,
        'nav_clientes': admin or mesero,
        'nav_empleados': admin,
        'nav_mesas': admin or mesero,
        'nav_platos': admin or mesero,
        'nav_ordenes': admin or mesero or cajero,
        'nav_facturas': admin or cajero,
        'nav_usuarios': admin,
        'nav_admin_site': user.is_authenticated and (user.is_staff or admin),
        'puede_crear_cliente': admin,
        'puede_editar_cliente': admin,
        'puede_eliminar_cliente': admin,
        'puede_crear_mesa': admin,
        'puede_editar_mesa': admin,
        'puede_eliminar_mesa': admin,
        'puede_crear_plato': admin,
        'puede_editar_plato': admin,
        'puede_eliminar_plato': admin,
        'puede_crear_orden': admin or mesero,
        'puede_editar_orden': admin or mesero,
        'puede_eliminar_orden': admin,
        'puede_crear_factura': admin or cajero,
        'puede_editar_factura': admin or cajero,
        'puede_eliminar_factura': admin,
        'dash_clientes': admin or mesero,
        'dash_empleados': admin,
        'dash_mesas': admin or mesero,
        'dash_platos': admin or mesero,
        'dash_ordenes': admin or mesero or cajero,
        'dash_facturas': admin or cajero,
    }
