from decimal import Decimal
from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        db_table = 'Cliente'

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    CARGOS = [
        ('Mesero', 'Mesero'),
        ('Mesera', 'Mesera'),
        ('Cajero', 'Cajero'),
        ('Cajera', 'Cajera'),
        ('Administrador', 'Administrador'),
    ]

    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50, choices=CARGOS)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        db_table = 'Empleado'

    def __str__(self):
        return f"{self.nombre} - {self.cargo}"


class Mesa(models.Model):
    ESTADOS_MESA = [
        ('Disponible', 'Disponible'),
        ('Ocupada', 'Ocupada'),
        ('Reservada', 'Reservada'),
    ]

    numero_mesa = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()
    estado_mesa = models.CharField(max_length=20, choices=ESTADOS_MESA, default='Disponible')

    class Meta:
        db_table = 'Mesa'

    def __str__(self):
        return f"Mesa {self.numero_mesa}"


class Plato(models.Model):
    nombre_plato = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    disponible = models.BooleanField(default=True)

    class Meta:
        db_table = 'Plato'

    def __str__(self):
        return self.nombre_plato


class Orden(models.Model):
    ESTADOS_ORDEN = [
        ('Activa', 'Activa'),
        ('En preparación', 'En preparación'),
        ('Entregada', 'Entregada'),
        ('Facturada', 'Facturada'),
        ('Cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado_orden = models.CharField(max_length=20, choices=ESTADOS_ORDEN, default='Activa')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'OrdenRestaurante'

    def __str__(self):
        return f"Orden {self.id} - {self.cliente.nombre}"

    def recalcular_total(self):
        total = sum((detalle.subtotal or Decimal('0.00')) for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])

    def resumen_platos(self, max_items=3):
        detalles = list(self.detalles.select_related('plato').all()[:max_items])
        if not detalles:
            return 'Sin platos'
        partes = [f'{d.plato.nombre_plato} x{d.cantidad}' for d in detalles]
        restantes = self.detalles.count() - len(partes)
        if restantes > 0:
            partes.append(f'+{restantes} más')
        return ', '.join(partes)


class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'Detalle_Orden'

    def save(self, *args, **kwargs):
        self.precio_unitario = self.plato.precio
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)
        self.orden.recalcular_total()

    def delete(self, *args, **kwargs):
        orden = self.orden
        super().delete(*args, **kwargs)
        orden.recalcular_total()

    def __str__(self):
        return f"{self.plato.nombre_plato} x{self.cantidad}"


class Factura(models.Model):
    METODOS_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Nequi', 'Nequi'),
        ('Daviplata', 'Daviplata'),
    ]

    orden = models.OneToOneField(Orden, on_delete=models.CASCADE)
    fecha_factura = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2)
    total_factura = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO)

    class Meta:
        db_table = 'Factura'

    def __str__(self):
        return f"Factura {self.id} - Orden {self.orden.id}"
