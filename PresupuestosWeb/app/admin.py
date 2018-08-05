from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import When, Case, Value, CharField, Q


class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedidoDetalle
    can_delete = True
    verbose_name_plural = 'Pedidos'


class NotaPedidoAdmin(admin.ModelAdmin):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine, )
    list_display = ('nroPedido','fecha','descripcionUso','estado')
    
    def get_queryset(self, request):
        queryset = super(NotaPedidoAdmin, self).get_queryset(request)
        if request.user.is_superuser: return queryset
        usuario = Usuario.objects.get(usuario=request.user)
        if not usuario: return queryset
        queryset1 = queryset.filter(departamentoDestino=usuario.departamentoSucursal).filter(estado='E')
        if queryset1.first(): return queryset1
        queryset = queryset.filter(departamentoOrigen=usuario.departamentoSucursal).filter(estado='B')
        #queryset = queryset.filter(
        #        estado = Case(
        #            When(departamentoOrigen==usuario.departamentoSucursal, then=Value('B') ),
        #            When(departamentoDestino==usuario.departamentoSucursal, then=Value('E') ),
        #        ),
        #    )
        return queryset

class NotaRemisionInLine(admin.TabularInline):
    model = NotaRemisionDetalle
    can_delete = True
    verbose_name_plural = 'Remisiones'


class NotaRemisionAdmin(admin.ModelAdmin):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaRemisionInLine, )
    list_display = ('nroRemision','fecha','nroPedido','estado')
    
    def get_queryset(self, request):
        queryset = super(NotaRemisionAdmin, self).get_queryset(request)
        if request.user.is_superuser: return queryset
        usuario = Usuario.objects.get(usuario=request.user)
        if not usuario: return queryset
        queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal, estado='B') | Q(departamentoDestino=usuario.departamentoSucursal, estado='E'))
        
        return queryset

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
admin.site.register(NotaRemision,NotaRemisionAdmin)
admin.site.register(Articulo)
admin.site.register(Departamento)
admin.site.register(Sucursal)
admin.site.register(DepartamentoSucursal)
admin.site.register(TipoArticulo)
admin.site.register(CategoriaArticulo)
admin.site.register(UnidadMedida)