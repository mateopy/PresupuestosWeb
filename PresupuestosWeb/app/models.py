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

ESTADOS_PEDIDO = (
        ('B', 'Borrador'),
        ('E', 'En Proceso'),
        ('R', 'Recepcionado'),
    )

class NotaPedido(models.Model):
    fecha = models.DateField('Fecha')
    nroPedido = models.IntegerField()
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_origen',on_delete=models.CASCADE)
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_destino',on_delete=models.CASCADE)
    precioAproximado = models.FloatField(default=0)
    descripcionUso = models.CharField(max_length=200)
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)


class NotaPedidoDetalle(models.Model):
    notaPedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE,null=True,blank=True)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE)


class NotaRemision(models.Model):
    fecha = models.DateField('Fecha')
    nroRemision = models.IntegerField()
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE)
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_origen',on_delete=models.CASCADE)
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_destino',on_delete=models.CASCADE)
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)


class NotaRemisionDetalle(models.Model):
    notaRemision = models.ForeignKey('NotaRemision',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE)

class Recepcion(models.Model):
    fecha = models.DateField('Fecha')
    nroRecepcion = models.IntegerField()
    remision = models.ForeignKey('NotaRemision',on_delete=models.CASCADE)
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_origen',on_delete=models.CASCADE)
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_destino',on_delete=models.CASCADE)
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)


class RecepcionDetalle(models.Model):
    recepcion = models.ForeignKey('Recepcion',on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo',on_delete=models.CASCADE)


class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    departamentoSucursal = models.ForeignKey('DepartamentoSucursal', on_delete=models.CASCADE)

#### TABLAS MENORES ####
class Articulo(models.Model):
    codigo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    tipoArticulo = models.ForeignKey('TipoArticulo',on_delete=models.CASCADE)
    unidadMedida = models.ForeignKey('UnidadMedida',on_delete=models.CASCADE)
    codigoBarras = models.CharField(max_length=50)
    categoria = models.ForeignKey('CategoriaArticulo',on_delete=models.CASCADE)
    precio = models.FloatField(default=0)
    observaciones = models.CharField(max_length=200)


class DepartamentoSucursal(models.Model):
    departamento = models.ForeignKey('Departamento',on_delete=models.CASCADE)
    sucursal = models.ForeignKey('Sucursal',on_delete=models.CASCADE)

class Departamento(models.Model):
    descripcion = models.CharField(max_length=50)
    

class Sucursal(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.IntegerField()

class TipoArticulo(models.Model):
    descripcion = models.CharField(max_length=50)

class CategoriaArticulo(models.Model):
    descripcion = models.CharField(max_length=50)

class UnidadMedida(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10)
