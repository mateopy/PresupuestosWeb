"""
Definition of models.
NOMENCLATURA:
NOMBRE DE CLASES: 
- Primera Letra Mayúscula
- La segunda palabra con la primera letra en mayúscula, sin guiones

NOMBRES DE ATRIBUTOS:
- Primera letra minúscula
- Segunda palabra con la primera letra en mayúscula, sin guiones

"""

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
import os

ESTADOS_PEDIDO = (
        ('B', 'Borrador'),
        ('PA', 'Pendiente de Aprobación'),
        ('E', 'En Proceso'),
        ('P', 'Procesado'),
    )

def get_file_path_presupuesto(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % ("Presupuesto-Pedido-", ext)
        return os.path.join('uploads/presupuestos', filename)

class FacturaCompra(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroFacturaCompra = models.IntegerField(verbose_name="Nro Factura Compra",blank=True, null=True)
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE, verbose_name="Nro Pedido")
    ordenCompra = models.ForeignKey('OrdenCompra',on_delete=models.CASCADE, verbose_name="Nro Orden Compra")
    proveedor = models.ForeignKey('Proveedor',on_delete=models.CASCADE,verbose_name="Proveedor")
    plazoPago = models.ForeignKey('PlazoPago',on_delete=models.CASCADE,verbose_name="Plazo de Pago")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    total = models.FloatField(default=0)
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Facturas de Compra"

    def __str__(self):
        return str(self.nroFacturaCompra)


class FacturaCompraDetalle(models.Model):
    facturaCompra = models.ForeignKey('FacturaCompra',on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE, verbose_name="Artículo")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción", null=True, blank=True)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,null=True,blank=True,verbose_name="Unidad de Medida")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    precio = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

class OrdenCompra(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroOrdenCompra = models.IntegerField(verbose_name="Nro Orden de Compra",blank=True, null=True)
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE, verbose_name="Nro Pedido")
    proveedor = models.ForeignKey('Proveedor',on_delete=models.CASCADE,verbose_name="Proveedor")
    fechaEntrega = models.DateField('Fecha Entrega',null=True,blank=True)
    terminosCondiciones = models.CharField(max_length=500, verbose_name="Términos y Condiciones", null=True, blank=True)
    plazoPago = models.ForeignKey('PlazoPago',on_delete=models.CASCADE,verbose_name="Plazo de Pago")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    observaciones = models.CharField(max_length=200, verbose_name="Observaciones", null=True, blank=True)
    total = models.FloatField(default=0)
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Órdenes de Compra"

    def __str__(self):
        return str(self.nroOrdenCompra)


class OrdenCompraDetalle(models.Model):
    notaCompra = models.ForeignKey('OrdenCompra',on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE, verbose_name="Artículo")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción", null=True, blank=True)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,null=True,blank=True,verbose_name="Unidad de Medida")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    precio = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

class SolicitudPresupuesto(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroPresupuesto = models.IntegerField(verbose_name="Nro Presupuesto",blank=True, null=True)
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE, verbose_name="Nro Pedido")
    proveedor = models.ForeignKey('Proveedor',on_delete=models.CASCADE,verbose_name="Proveedor")
    fechaEntrega = models.DateField('Fecha Entrega',null=True,blank=True)
    terminosCondiciones = models.CharField(max_length=500, verbose_name="Términos y Condiciones", null=True, blank=True)
    plazoPago = models.ForeignKey('PlazoPago',on_delete=models.CASCADE,verbose_name="Plazo de Pago")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    total = models.FloatField(default=0)
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Solicitudes de Presupuesto"

    def __str__(self):
        return str(self.nroPresupuesto)


class SolicitudPresupuestoDetalle(models.Model):
    solicitudPresupuesto = models.ForeignKey('SolicitudPresupuesto',on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE, verbose_name="Artículo")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción", null=True, blank=True)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,null=True,blank=True,verbose_name="Unidad de Medida")
    moneda = models.ForeignKey('Moneda',on_delete=models.CASCADE,verbose_name="Moneda")
    precio = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)
    


class NotaPedido(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroPedido = models.IntegerField(verbose_name="Nro Pedido",blank=True, null=True)
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    precioAproximado = models.CharField(max_length=200, verbose_name="Precio Aproximado", null=True, blank=True)
    descripcionUso = models.CharField(max_length=200, verbose_name="Descripción Uso", null=True, blank=True)
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Notas de Pedido"

    def __str__(self):
        return str(self.nroPedido)


class NotaPedidoDetalle(models.Model):
    notaPedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,null=True,blank=True,verbose_name="Unidad de Medida")
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE, verbose_name="Artículo")

    class Meta:
        verbose_name_plural = "Detalles"
        verbose_name = "Artículo"

class NotaPedidoPresupuesto(models.Model):
    notaPedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE)
    presupuesto = models.FileField(upload_to=get_file_path_presupuesto,null=True,blank=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Presupuestos"
        verbose_name = "Presupuesto"

class NotaPedidoAutorizador(models.Model):
    notaPedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    fechaAutorizacion = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    ip = models.CharField(max_length=15,blank=True,null=True)
    dispositivo = models.CharField(max_length=50,blank=True,null=True)
    gps = models.CharField(max_length=50,blank=True,null=True)
    hashAutorizacion = models.CharField(max_length=32)

class NotaRemision(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroRemision = models.IntegerField(verbose_name="Nro Remisión",blank=True, null=True)
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE, verbose_name="Nro Pedido")
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Notas de Remisión"

    def __str__(self):
        return str(self.nroRemision) + " - " + str(self.pedido.nroPedido)

    def nroPedido(self):
        return self.pedido.nroPedido


class NotaRemisionDetalle(models.Model):
    notaRemision = models.ForeignKey('NotaRemision',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,verbose_name="Unidad de Medida")
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE)

class Recepcion(models.Model):
    fecha = models.DateField('Fecha', default=timezone.localtime(timezone.now()))
    nroRecepcion = models.IntegerField(verbose_name="Nro Recepción",blank=True, null=True)
    remision = models.ForeignKey('NotaRemision',on_delete=models.CASCADE)
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    estado = models.CharField(max_length=2,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Recepciones"


class RecepcionDetalle(models.Model):
    recepcion = models.ForeignKey('Recepcion',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE, verbose_name="Unidad de Medida")
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE)


class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    departamentoSucursal = models.ForeignKey('DepartamentoSucursal', on_delete=models.CASCADE)

#### TABLAS MENORES ####
class Articulo(models.Model):
    codigo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    tipoArticulo = models.ForeignKey('TipoArticulo',on_delete=models.CASCADE, verbose_name="Tipo de Artículo")
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE, verbose_name="Unidad de Medida")
    codigoBarras = models.CharField(max_length=50, verbose_name="Código de Barras",blank=True,null=True)
    categoria = models.ForeignKey('CategoriaArticulo',on_delete=models.CASCADE)
    codigoActivoFijo = models.CharField(max_length=50, verbose_name="Código Activo Fijo")
    precio = models.FloatField(default=0)
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.codigo + " - " + self.descripcion

class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    ruc = models.CharField(max_length=20, verbose_name="RUC")
    direccion = models.CharField(max_length=100, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(max_length=50, verbose_name="E-mail")
    nombreContacto = models.CharField(max_length=50, verbose_name="Nombre Contacto")
    telefonoContacto = models.CharField(max_length=50, verbose_name="Teléfono Contacto")
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.ruc + " - " + self.nombre

    class Meta:
        verbose_name_plural = "Proveedores"


class DepartamentoSucursal(models.Model):
    departamento = models.ForeignKey('Departamento',on_delete=models.CASCADE)
    sucursal = models.ForeignKey('Sucursal',on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Departamentos por Sucursal"
      
    def __str__(self):
        return (str((self.departamento.descripcion)) + " - " + self.sucursal.descripcion)

class DepartamentoSucursalAutorizador(models.Model):
    departamentoSucursal = models.ForeignKey('DepartamentoSucursal',on_delete=models.CASCADE)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    

    class Meta:
        verbose_name_plural = "Autorizadores por Departamento-Sucursal"
        verbose_name = "Autorizador"
      
    def __str__(self):
        return self.usuario.username
    

class Departamento(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return self.descripcion

class Moneda(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.CharField(max_length=5)

    class Meta:
        verbose_name_plural = "Monedas"

    def __str__(self):
        return self.descripcion

class Sucursal(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.IntegerField()

    class Meta:
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.descripcion

class PlazoPago(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Plazos de Pago"

    def __str__(self):
        return self.descripcion

class TipoArticulo(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Tipos de Artículo"

    def __str__(self):
        return self.descripcion

class CategoriaArticulo(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categorias de Artículo"

    def __str__(self):
        return self.descripcion

class UnidadMedida(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Unidades de Medida"

    def __str__(self):
        return self.descripcion
