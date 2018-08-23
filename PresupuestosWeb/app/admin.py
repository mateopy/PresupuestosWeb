from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q, Max
from django.utils.html import format_html
from django.urls import reverse, path
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.forms import HiddenInput
import datetime
from app.forms import PedidoForm
import app.views
import app.reports


class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedidoDetalle
    can_delete = True
    verbose_name_plural = 'Pedidos'
    #fields = ('notaPedido','cantidad','unidadMedida','articulo')
    fields = ('notaPedido','articulo','cantidad','unidadMedida')



class NotaPedidoAdmin(admin.ModelAdmin):
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    READ_ONLY = False
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine,)
    fields = ('fecha','usuario','nroPedido','departamentoOrigen','departamentoDestino','precioAproximado','descripcionUso','estado')
    list_display = ('nroPedido','fecha','departamentoOrigen','departamentoDestino','descripcionUso','estado','accion_pedido')
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']
    readonly_fields = ('fecha','estado')
    ordering = ['nroPedido']
    actions = ['generar_remision']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:notapedido_id>)/', self.admin_site.admin_view(self.procesar_pedido), name='pedido_enviar'),
            path('imprimir/<int:notapedido_id>', app.reports.nota_pedido_report, name='pedido_imprimir'),]
        return custom_urls + urls
    
    def get_form(self, request, obj = None, **kwargs):
        form = super(NotaPedidoAdmin, self).get_form(request, obj, **kwargs) 
        if (form.base_fields):
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
                form.base_fields['usuario'].widget = HiddenInput()
            if not (form.base_fields['departamentoOrigen'].initial):
                form.base_fields['departamentoOrigen'].initial = request.user.usuario.departamentoSucursal.pk
                form.base_fields['departamentoOrigen'].disabled = True
                form.base_fields['departamentoOrigen'].widget.can_add_related = False
                form.base_fields['departamentoOrigen'].widget.can_change_related = False
            if not (form.base_fields['nroPedido'].initial):
                form.base_fields['nroPedido'].initial = self.get_max_nroPedido(request)
                form.base_fields['nroPedido'].disabled = True
        return form

    def get_max_nroPedido(self, request):
        #qpedido = NotaPedido.objects.annotate(Max('nroPedido')).filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal)
        try:
            qpedido = NotaPedido.objects.filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal).latest('nroPedido')
        except:
            qpedido = None
        if qpedido:
            nropedido = int(qpedido.nroPedido+1)
        else:
           nropedido = int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1

        return nropedido

    # metodo para agregar el boton en el list del pedido
    def accion_pedido(self, obj):
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" target="_blank" href="{}">Imprimir</a>',
            reverse('admin:pedido_enviar', args=[obj.pk]),
            reverse('admin:pedido_imprimir', args=[obj.pk]),)
    accion_pedido.short_description = 'Procesar'
    accion_pedido.allow_tags = True

    #metodo para cambiar procesar los pedidos
    def procesar_pedido(self, request, notapedido_id, *args, **kwargs):
        pedido = self.get_object(request, notapedido_id)
        if (pedido):
            if (pedido.estado == self.BORRADOR):
                pedido.estado = self.EN_PROCESO
                pedido.save()
            else:
                self.message_user(request, "Pedido Ya Procesado")
        url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    
    #metodo para imprimir el pedido
    def imprimir_pedido(self, request, notapedido_id, *args, **kwargs):
        pedido = self.get_object(request, notapedido_id)
        if (pedido and pedido.estado != self.BORRADOR):
            pass
        url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def has_add_permission(self, request):
        if self.READ_ONLY:
            return False
        return super(NotaPedidoAdmin, self).has_add_permission(request)

    #def has_delete_permission(self, request, obj = None):
    #    if self.READ_ONLY:
    #        return False
    #    return super(NotaPedidoAdmin, self).has_delete_permission(request, obj)

    def changelist_view(self, request, extra_context = None):
        self.READ_ONLY = False
        self.readonly_fields = ('fecha','estado')
        for inline in self.inlines:
            inline.readonly_fields = []
        return super(NotaPedidoAdmin, self).changelist_view(request, extra_context)

    #def add_view(self, request, form_url = '', extra_context = None):
    #    self.readonly_fields = ('fecha, estado')
    #    return super(NotaPedidoAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):

        pedido = self.get_object(request, object_id)
        #if request.user.is_superuser: return super(NotaPedidoAdmin,
        #self).change_view(request, object_id, form_url,
        #extra_context=extra_context)
        self.READ_ONLY = False
        if (pedido and pedido.estado != self.BORRADOR):
            self.READ_ONLY = True
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_delete'] = False
            extra_context['show_save'] = False
            extra_context['show_save_and_add_another'] = False
            variables = []
            for field in self.get_fields(request):
                variables.append(field)
            self.readonly_fields = tuple(variables)

            for inline in self.inlines:
                inline.readonly_fields = tuple(inline.get_fields(inline, request))
        else:
            self.readonly_fields = ('fecha', 'estado') #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = []#inline.get_readonly_fields(inline, request)
        return super(NotaPedidoAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
    
    
    def get_queryset(self, request):
        queryset = super(NotaPedidoAdmin, self).get_queryset(request)
        if request.user.is_superuser: return queryset
        usuario = Usuario.objects.get(usuario=request.user)
        if not usuario: return queryset
        #queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal, estado='B') | Q(departamentoDestino=usuario.departamentoSucursal, estado='E'))
        queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal) | Q(departamentoDestino=usuario.departamentoSucursal, estado='E'))
 
        return queryset

    def generar_remision(self, request, queryset):
        contador = 0
        for pedido in queryset:
            try:
                remision = NotaRemision()
                remision.fecha = datetime.date.today()
                remision.nroRemision = NotaRemisionAdmin.get_max_nroRemision(self, request)
                remision.pedido = pedido
                remision.departamentoOrigen = pedido.departamentoDestino
                remision.departamentoDestino = pedido.departamentoOrigen
                remision.estado = self.BORRADOR
                remision.usuario = request.user
                remision.save()
                for inline in pedido.notapedidodetalle_set.all():
                    detalle = NotaRemisionDetalle()
                    detalle.notaRemision = remision
                    detalle.cantidad = inline.cantidad
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.save()
                contador+=1
            except:
                self.message_user(request, "Ocurrio un error durante la generacion, verificar Pedidos")
        if contador == 1:
            mensaje = "1 Remision Generada"
        else:
            mensaje = "%s Remisiones Generadas " % contador
        self.message_user(request,"%s Satisfactoriamente" % mensaje)
    generar_remision.short_description = "Generar Remision/es"

class NotaRemisionInLine(admin.TabularInline):
    model = NotaRemisionDetalle
    can_delete = True
    verbose_name_plural = 'Remisiones'
    #fields = ('notaRemision','cantidad','unidadMedida','articulo')
    fields = ('notaRemision','articulo','cantidad','unidadMedida')


class NotaRemisionAdmin(admin.ModelAdmin):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    READ_ONLY = False
    inlines = (NotaRemisionInLine,)
    fields = ('fecha','usuario','nroRemision','pedido','departamentoOrigen','departamentoDestino','estado')
    list_display = ('nroRemision','fecha','nroPedido','departamentoOrigen','departamentoDestino','estado','accion_remision')
    readonly_fields = ('fecha','estado')
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']
    ordering = ['nroRemision']
    actions = ['generar_recepcion']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:notaremision_id>)/', self.admin_site.admin_view(self.procesar_remision), name='remision_enviar'),
            path('imprimir/(<int:notaremision_id>)/', self.admin_site.admin_view(self.imprimir_remision), name='remision_imprimir'),]
        return custom_urls + urls

    def accion_remision(self, obj):
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" href="{}">Imprimir</a>',
            reverse('admin:remision_enviar', args=[obj.pk]),
            reverse('admin:remision_imprimir', args=[obj.pk]),)
    accion_remision.short_description = 'Procesar'
    accion_remision.allow_tags = True

    #metodo para cambiar procesar los pedidos
    def procesar_remision(self, request, notaremision_id, *args, **kwargs):
        remision = self.get_object(request, notaremision_id)
        if (remision):
            if (remision.estado == self.BORRADOR):
                remision.estado = self.EN_PROCESO
                remision.save()
            else:
                self.message_user(request, "Remision Ya Procesada")
        url = reverse('admin:app_notaremision_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    
    #metodo para imprimir el pedido
    def imprimir_remision(self, request, notaremision_id, *args, **kwargs):
        remision = self.get_object(request, notaremision_id)
        if (remision and remision.estado != self.BORRADOR):
            pass
        url = reverse('admin:app_notaremision_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def get_form(self, request, obj = None, **kwargs):
        form = super(NotaRemisionAdmin, self).get_form(request, obj, **kwargs) 
        if (form.base_fields):
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
                form.base_fields['usuario'].widget = HiddenInput()
            if not (form.base_fields['departamentoOrigen'].initial):
                form.base_fields['departamentoOrigen'].initial = request.user.usuario.departamentoSucursal.pk
                form.base_fields['departamentoOrigen'].disabled = True
                form.base_fields['departamentoOrigen'].widget.can_add_related = False
                form.base_fields['departamentoOrigen'].widget.can_change_related = False
            if not (form.base_fields['nroRemision'].initial):
                form.base_fields['nroRemision'].initial = self.get_max_nroRemision(request)
                form.base_fields['nroRemision'].disabled = True
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        pedido = self.get_object(request, object_id)
        self.READ_ONLY = False
        if (pedido and pedido.estado != self.BORRADOR):
            self.READ_ONLY = True
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_delete'] = False
            extra_context['show_save'] = False
            extra_context['show_save_and_add_another'] = False
            variables = []
            for field in self.get_fields(request):
                variables.append(field)
            self.readonly_fields = tuple(variables)

            for inline in self.inlines:
                inline.readonly_fields = tuple(inline.get_fields(inline, request))
        else:
            self.readonly_fields = ('fecha', 'estado') #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = []#inline.get_readonly_fields(inline, request)
        return super(NotaRemisionAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        if self.READ_ONLY:
            return False
        return super(NotaRemisionAdmin, self).has_add_permission(request)

    def changelist_view(self, request, extra_context = None):
        self.READ_ONLY = False
        self.readonly_fields = ('fecha','estado')
        for inline in self.inlines:
            inline.readonly_fields = []
        return super(NotaRemisionAdmin, self).changelist_view(request, extra_context)

    def get_queryset(self, request):
        queryset = super(NotaRemisionAdmin, self).get_queryset(request)
        if request.user.is_superuser: return queryset
        usuario = Usuario.objects.get(usuario=request.user)
        if not usuario: return queryset
        #queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal, estado='B') | Q(departamentoDestino=usuario.departamentoSucursal, estado='E'))
        queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal) | Q(departamentoDestino=usuario.departamentoSucursal))
        
        return queryset

    def get_max_nroRemision(self, request):
        try:
            qremision = NotaRemision.objects.filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal).latest('nroRemision')
        except:
            qremision = None
        if qremision:
            nroRemision = int(qremision.nroRemision+1)
        else:
            nroRemision = int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1

        return nroRemision

    def generar_recepcion(self, request, queryset):
        contador = 0
        for remision in queryset:
            try:
                recepcion = Recepcion()
                recepcion.fecha = datetime.date.today()
                recepcion.nroRecepcion = RecepcionAdmin.get_max_nroRecepcion(self, request)
                recepcion.remision = remision
                recepcion.departamentoOrigen = remision.departamentoDestino
                recepcion.departamentoDestino = remision.departamentoOrigen
                recepcion.estado = self.BORRADOR
                recepcion.usuario = request.user
                recepcion.save()
                for inline in recepcion.recepciondetalle_set.all():
                    detalle = RecepcionDetalle()
                    detalle.recepcion = recepcion
                    detalle.cantidad = inline.cantidad
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.save()
                contador+=1
            except Exception as e:
                #self.message_user(request, str(e))
                self.message_user(request, "Ocurrio un error durante la generacion, verificar remision/es")
        if contador == 1:
            mensaje = "1 Recepcion Generada"
        else:
            mensaje = "%s Recepciones Generadas " % contador
        self.message_user(request,"%s Satisfactoriamente" % mensaje)
    generar_recepcion.short_description = "Generar Recepcion/es"

class RecepcionInLine(admin.TabularInline):
    model = RecepcionDetalle
    can_delete = True
    verbore_name_plural = 'Recepciones'

class RecepcionAdmin(admin.ModelAdmin):
    inlines = (RecepcionInLine,)
    list_display = ('nroRecepcion','fecha','remision','departamentoOrigen','departamentoDestino','estado')
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']


    def get_max_nroRecepcion(self, request):
        try:
            qrecepcion = Recepcion.objects.filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal).latest('nroRecepcion')
        except:
            qrecepcion = None
        if qrecepcion:
            nroRecepcion = int(qrecepcion.nroRecepcion+1)
        else:
            nroRecepcion = int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1

        return nroRecepcion

class UsuarioInLine(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Perfiles'

class UsuarioAdmin(UserAdmin):
    inlines = (UsuarioInLine,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(NotaPedido,NotaPedidoAdmin)
admin.site.register(NotaRemision,NotaRemisionAdmin)
admin.site.register(Recepcion, RecepcionAdmin)
admin.site.register(Articulo)
admin.site.register(Departamento)
admin.site.register(Sucursal)
admin.site.register(DepartamentoSucursal)
admin.site.register(TipoArticulo)
admin.site.register(CategoriaArticulo)
admin.site.register(UnidadMedida)