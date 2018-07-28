"""
Definition of models.
NOMENCLATURA:
Nombres de las clases: 
"""

from django.db import models
from django.contrib.auth.models import User

ESTADOS_PEDIDO = (
        ('B', 'Borrador'),
        ('E', 'En Proceso'),
        ('R', 'Recepcionado'),
        
    )

class NotaPedido(models.Model):
    fecha = models.DateTimeField('Fecha')
    nroPedido = models.IntegerField()
    usuario = models.ForeignKey(User)
    origen = models.ForeignKey('Dependencia', related_name='dependencia_origen')
    destino = models.ForeignKey('Dependencia', related_name='dependencia_destino')
    precioAproximado = models.FloatField(default=0)
    descripcionUso = models.CharField(max_length=200)
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')


class NotaPedido_Detalle(models.Model):
    notaPedido = models.ForeignKey('NotaPedido')
    cantidad = models.IntegerField()
    articulo = models.ForeignKey('Articulo')


class Articulo(models.Model):
    codigo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    tipoArticulo = models.ForeignKey('TipoArticulo')
    codigoBarras = models.CharField(max_length=50)
    categoria = models.ForeignKey('CategoriaArticulo')
    precio = models.FloatField(default=0)
    observaciones = models.CharField(max_length=200)


#### TABLAS MENORES ####
class Dependencia(models.Model):
    descripcion = models.CharField(max_length=50)
    sucursal = models.ForeignKey('Sucursal')

class Sucursal(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.IntegerField()

class TipoArticulo(models.Model):
    descripcion = models.CharField(max_length=50)

class CategoriaArticulo(models.Model):
    descripcion = models.CharField(max_length=50)
