from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard


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
    columns = 3

    def init_with_context(self, context):
        #self.available_children = None
        #self.available_children.append(modules.Feed)
        self.available_children.append(modules.LinkList)

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Operaciones'),
            models=('app.NotaPedido','app.NotaRemision','app.Recepcion','app.SolicitudPresupuesto'),
            column=0,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Datos Generales'),
            models=('app.Sucursal','app.Departamento','app.DepartamentoSucursal','app.Proveedor','app.PlazoPago'),
            column=1,
            order=0
        ))

        self.children.append(modules.ModelList(
            _('Articulos'),
            models=('app.Articulo','app.CategoriaArticulo','app.TipoArticulo','app.UnidadMedida'),
            column=2,
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
    columns = 3
    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)

        self.children.append(modules.ModelList(
            _('Operaciones'),
            models=('app.NotaPedido','app.NotaRemision','app.Recepcion','app.SolicitudPresupuesto'),
            column=0,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Datos Generales'),
            models=('app.Sucursal','app.Departamento','app.DepartamentoSucursal','app.Proveedor','app.PlazoPago'),
            column=1,
            order=0
        ))

        self.children.append(modules.ModelList(
            _('Articulos'),
            models=('app.Articulo','app.CategoriaArticulo','app.TipoArticulo','app.UnidadMedida'),
            column=2,
            order=0
        ))

        # append an app list module for "Administration"
        #self.children.append(modules.ModelList(
        #    _('Administration'),
        #    models=('auth.*',),
        #    column=1,
        #    order=0
        #))