from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import When, Case, Value, CharField, Q
from django.utils.html import format_html
from django.urls import reverse, path
from django.conf.urls import url
from django.http import HttpResponseRedirect


class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedidoDetalle
    can_delete = True
    verbose_name_plural = 'Pedidos'

class NotaPedidoAdmin(admin.ModelAdmin):
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine,)
    list_display = ('nroPedido','fecha','descripcionUso','estado','accion_pedido')
    ordering = ['nroPedido']
    actions = ['actualizar_estado']

    #list_select_related = ('usuario',)

    #metodo para actualizar de forma masiva los pedidos marcados
    def actualizar_estado(self, request, queryset):
        filas = queryset.update(estado = self.EN_PROCESO)
        if filas == 1:
            mensaje = "1 Pedido Procesado"
        else:
            mensaje = "%s Pedidos Procesados " %filas
        self.message_user(request, "%s Satisfacoriamente" %mensaje)
    actualizar_estado.short_description = "Procesar Pedidos"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            #url(r'^$', app.views.home, name='home')
            path('procesar/(<int:notapedido_id>)/', self.admin_site.admin_view(self.procesar_pedido), name='pedido_enviar')
        ]
        return custom_urls + urls

    # metodo para agregar el boton en el list del pedido
    def accion_pedido(self, obj):
        return format_html(
            '<a class="button" href="{}">Enviar</a>&nbsp;',
            reverse('admin:pedido_enviar', args=[obj.pk]),
        )
    accion_pedido.short_description = 'Procesar'
    accion_pedido.allow_tags = True

    #metodo para cambiar el estado de los pedidos en borrador
    def procesar_pedido(self, request, notapedido_id, *args, **kwargs):
        pedido = self.get_object(request, notapedido_id)
        if (pedido and pedido.estado == self.BORRADOR):
            pedido.estado = self.EN_PROCESO
            pedido.save()
            url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
            return HttpResponseRedirect(url)
        #return request

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