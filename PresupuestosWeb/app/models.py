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

ESTADOS_PEDIDO = (
        ('B', 'Borrador'),
        ('E', 'En Proceso'),
        ('P', 'Procesado'),
    )

class NotaPedido(models.Model):
    fecha = models.DateField('Fecha', default=datetime.now)
    nroPedido = models.IntegerField(verbose_name="Nro Pedido")
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='pedido_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    precioAproximado = models.CharField(max_length=200, verbose_name="Precio Aproximado", null=True, blank=True)
    descripcionUso = models.CharField(max_length=200, verbose_name="Descripción Uso", null=True, blank=True)
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
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


class NotaRemision(models.Model):
    fecha = models.DateField('Fecha', default=datetime.now)
    nroRemision = models.IntegerField(verbose_name="Nro Remisión")
    pedido = models.ForeignKey('NotaPedido',on_delete=models.CASCADE, verbose_name="Nro Pedido")
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='remision_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
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
    fecha = models.DateField('Fecha', default=datetime.now)
    nroRecepcion = models.IntegerField(verbose_name="Nro Recepción")
    remision = models.ForeignKey('NotaRemision',on_delete=models.CASCADE)
    departamentoOrigen = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_origen',on_delete=models.CASCADE, verbose_name="Departamento Origen")
    departamentoDestino = models.ForeignKey('DepartamentoSucursal', related_name='recepcion_departamento_destino',on_delete=models.CASCADE, verbose_name="Departamento Destino")
    estado = models.CharField(max_length=1,choices=ESTADOS_PEDIDO,default='B')
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
    codigoBarras = models.CharField(max_length=50, verbose_name="Código de Barras")
    categoria = models.ForeignKey('CategoriaArticulo',on_delete=models.CASCADE)
    precio = models.FloatField(default=0)
    observaciones = models.CharField(max_length=200)

    def __str__(self):
        return self.codigo + " - " + self.descripcion


class DepartamentoSucursal(models.Model):
    departamento = models.ForeignKey('Departamento',on_delete=models.CASCADE)
    sucursal = models.ForeignKey('Sucursal',on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Departamentos por Sucursal"
       
    def __str__(self):
        return (str((self.departamento.descripcion)) + " - " + self.sucursal.descripcion)

class Departamento(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return self.descripcion
    

class Sucursal(models.Model):
    descripcion = models.CharField(max_length=50)
    codigo = models.IntegerField()

    class Meta:
        verbose_name_plural = "Sucursales"

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
