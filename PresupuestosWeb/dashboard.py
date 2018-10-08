from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

from jet.dashboard.modules import DashboardModule
from app.models import NotaPedido
from app.models import NotaRemision
from app.models import Recepcion
from django.db.models import Q



#class CustomIndexDashboard(Dashboard):
#    columns = 3
#    def init_with_context(self, context):
#        self.children.append(modules.ModelList(
#            _('Operaciones'),
#            models = ('app.notapedido','app.notaremision','app.recepcion'),
#            column = 0,
#            order = 0
#            ))


class CustomIndexDashboard(Dashboard):
    columns = 4

    def init_with_context(self, context):
        #self.available_children = None
        #self.available_children.append(modules.Feed)
        self.available_children.append(modules.LinkList)

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Pedidos'),
            models=('app.NotaPedido','app.NotaRemision','app.Recepcion',),
            column=0,
            order=1
        ))
        self.children.append(modules.ModelList(
            _('Compras'),
            models=('app.SolicitudPresupuesto','app.OrdenCompra','app.FacturaCompra',),
            column=1,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Articulos'),
            models=('app.Articulo','app.CategoriaArticulo','app.TipoArticulo','app.UnidadMedida'),
            column=2,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Mantenimiento'),
            models=('app.Sucursal','app.Departamento','app.DepartamentoSucursal','app.Proveedor','app.PlazoPago'),
            column=3,
            order=0
        ))

        self.children.append(PedidosPendientes(
             column=0,
            order=0
            ))
        # append an app list module for "Administration"
        #self.children.append(modules.ModelList(
        #    _('Administration'),
        #    models=('auth.*',),
        #    column=1,
        #    order=0
        #))

        # append a recent actions module
        #self.children.append(modules.RecentActions(
        #    _('Recent Actions'),
        #    10,
        #    column=0,
        #    order=1
        #))


class CustomAppIndexDashboard(AppIndexDashboard):
    columns = 4
    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)

        self.children.append(modules.ModelList(
            _('Pedidos'),
            models=('app.NotaPedido','app.NotaRemision','app.Recepcion','app.SolicitudPresupuesto'),
            column=0,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Compras'),
            models=('app.SolicitudPresupuesto','app.OrdenCompra','app.FacturaCompra','app.Proveedor'),
            column=3,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Articulos'),
            models=('app.Articulo','app.CategoriaArticulo','app.TipoArticulo','app.UnidadMedida'),
            column=2,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Datos Maestros'),
            models=('app.Sucursal','app.Departamento','app.DepartamentoSucursal','app.Proveedor','app.PlazoPago'),
            column=1,
            order=0
        ))

        

        # append an app list module for "Administration"
        #self.children.append(modules.ModelList(
        #    _('Administration'),
        #    models=('auth.*',),
        #    column=1,
        #    order=0
        #))

class PedidosPendientes(DashboardModule):
    title = 'Pedidos Pendientes'
    title_url = '/'
    template = 'app/module.html'
    limit = 10

    def init_with_context(self, context):
        usuario=self.context['request'].user
        username = usuario.first_name
        cantPedidos = NotaPedido.objects.filter(Q(departamentoOrigen=usuario.usuario.departamentoSucursal) | Q(Q(departamentoDestino=usuario.usuario.departamentoSucursal), ~Q(estado='E'))).count()
        cantRemisiones = NotaRemision.objects.all().count()
        cantRecepciones = Recepcion.objects.all().count()
        totales = {
            'username': username, 
            'cantPedidos':cantPedidos, 
            'cantRemisiones':cantRemisiones, 
            'cantRecepciones':cantRecepciones
            }
        self.children = totales

