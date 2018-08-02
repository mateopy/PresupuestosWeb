from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedidoDetalle
    can_delete = True
    verbose_name_plural = 'Pedidos'


class NotaPedidoAdmin(admin.ModelAdmin):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine, )

class UsuarioInLine(admin.StackedInline):
    model = Usuario
    can_delete=False
    verbose_name_plural = 'Perfiles'

class UsuarioAdmin(UserAdmin):
    inlines = (UsuarioInLine, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(NotaPedido,NotaPedidoAdmin)
admin.site.register(Articulo)
admin.site.register(Departamento)
admin.site.register(Sucursal)
admin.site.register(DepartamentoSucursal)
admin.site.register(TipoArticulo)
admin.site.register(CategoriaArticulo)
admin.site.register(UnidadMedida)