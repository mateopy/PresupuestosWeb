from app.models import *
from django.contrib import admin

class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedido_Detalle
    can_delete = True
    verbose_name_plural = 'Pedidos'


class NotaPedidoAdmin(admin.ModelAdmin):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine, )

# Re-register UserAdmin
admin.site.register(NotaPedido,NotaPedidoAdmin)