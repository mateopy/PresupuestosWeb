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
from django.utils import timezone
from app.forms import PedidoForm
import app.views
import app.reports

#HERENCIA
class Nota(admin.ModelAdmin):
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    PROCESADO = 'P'
    READ_ONLY = False

    def has_add_permission(self, request):
        if self.READ_ONLY:
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context = None):
        self.READ_ONLY = False
        self.readonly_fields = ('fecha','estado')
        for inline in self.inlines:
            inline.readonly_fields = []
            inline.can_delete = True
            inline.max_num = None
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser: return queryset
        usuario = Usuario.objects.get(usuario=request.user)
        if not usuario: return queryset
        #queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal, estado='B') | Q(departamentoDestino=usuario.departamentoSucursal, estado='E'))
        queryset = queryset.filter(Q(departamentoOrigen=usuario.departamentoSucursal) | Q(Q(departamentoDestino=usuario.departamentoSucursal), ~Q(estado='B')))
 
        return queryset

    def change_view(self, request, object_id, form_url='', extra_context=None):
        objecto = self.get_object(request, object_id)
        self.READ_ONLY = False
        if (objecto and objecto.estado != self.BORRADOR):
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
                inline.can_delete = False
                inline.max_num = 0
        else:
            self.readonly_fields = ('fecha', 'estado') #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = []#inline.get_readonly_fields(inline, request)
                inline.can_delete = True
                inline.max_num = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if (form.base_fields):
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
                form.base_fields['usuario'].widget = HiddenInput()
            if not (form.base_fields['departamentoOrigen'].initial):
                form.base_fields['departamentoOrigen'].initial = request.user.usuario.departamentoSucursal.pk
                form.base_fields['departamentoOrigen'].disabled = True
                form.base_fields['departamentoOrigen'].widget.can_add_related = False
                form.base_fields['departamentoOrigen'].widget.can_change_related = False
        return form

    def get_max_object(self, request, modelo, campo):
        #qpedido = NotaPedido.objects.annotate(Max('nroPedido')).filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal)
        try:
            lastObjeto = modelo.objects.filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal).latest(campo)
        except:
            lastObjeto = None

        return lastObjeto

class NotaPedidoInLine(admin.TabularInline):
    model = NotaPedidoDetalle
    can_delete = True
    verbose_name_plural = 'Pedidos'
    #fields = ('notaPedido','cantidad','unidadMedida','articulo')
    fields = ('notaPedido','articulo','cantidad','unidadMedida')
    extra = 2

class NotaPedidoAdmin(Nota):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine,)
    fields = ('fecha','usuario','nroPedido','departamentoOrigen','departamentoDestino','precioAproximado','descripcionUso','estado')
    list_display = ('nroPedido','fecha','departamentoOrigen','departamentoDestino','descripcionUso','estado','accion_pedido')
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']
    readonly_fields = ('fecha','estado')
    ordering = ['nroPedido']
    actions = ['generar_remision','procesar']

    def procesar(self, request, queryset):
        contador = 0
        for objeto in queryset:
            if (objeto.estado == self.EN_PROCESO):
                objeto.estado = self.PROCESADO
                objeto.save()
                contador += 1
        if contador == 0:
            self.message_user(request, "No se proceso ningun pedido, verificar estado")
        if contador == 1:
            self.message_user(request, "Se proceso %s nota de pedido" %contador)
        if contador > 1:
            self.message_user(request, "Se procesaron %s notas de pedidos" %contador)
        url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    procesar.short_description = "Actualizar Estado A Procesado"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:notapedido_id>)/', self.admin_site.admin_view(self.enviar_pedido), name='pedido_enviar'),
            path('imprimir/<int:notapedido_id>', app.reports.nota_pedido_report, name='pedido_imprimir'),]
        return custom_urls + urls
    
    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs) 
        if (not obj and form.base_fields):
            if not (form.base_fields['nroPedido'].initial):
                form.base_fields['nroPedido'].initial = 0
                form.base_fields['nroPedido'].disabled = True
        return form


    # metodo para agregar el boton en el list del pedido
    def accion_pedido(self, obj):
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" target="_blank" href="{}">Imprimir</a>',
            reverse('admin:pedido_enviar', args=[obj.pk]),
            reverse('admin:pedido_imprimir', args=[obj.pk]),)
    accion_pedido.short_description = 'Procesar'
    accion_pedido.allow_tags = True

    #metodo para cambiar procesar los pedidos
    def enviar_pedido(self, request, notapedido_id, *args, **kwargs):
        pedido = self.get_object(request, notapedido_id)
        if (pedido):
            if (pedido.estado == self.BORRADOR):
                pedido.estado = self.EN_PROCESO
                lastObject = self.get_max_object(request, NotaPedido, 'nroPedido')
                pedido.nroPedido = int(lastObject.nroPedido+1) if lastObject else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                pedido.save()
            else:
                self.message_user(request, "Pedido ya se encuentra en proceso")
        url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def generar_remision(self, request, queryset):
        contador = 0
        for pedido in queryset:
            try:
                remision = NotaRemision()
                remision.fecha = timezone.localtime(timezone.now())
                remision.nroRemision = 0
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
                NotaPedido.objects.filter(nroPedido=pedido.nroPedido).update(estado=self.PROCESADO,fecha=timezone.localtime(timezone.now()))
            except Exception as e:
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
    extra = 2
    verbose_name_plural = 'Remisiones'
    #fields = ('notaRemision','cantidad','unidadMedida','articulo')
    fields = ('notaRemision','articulo','cantidad','unidadMedida')


class NotaRemisionAdmin(Nota):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaRemisionInLine,)
    fields = ('fecha','usuario','nroRemision','pedido','departamentoOrigen','departamentoDestino','estado')
    list_display = ('nroRemision','fecha','nroPedido','departamentoOrigen','departamentoDestino','estado','accion_remision')
    readonly_fields = ('fecha','estado')
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']
    ordering = ['nroRemision']
    actions = ['generar_recepcion','procesar']
    
    def procesar(self, request, queryset):
        contador = 0
        for objeto in queryset:
            if (objeto.estado == self.EN_PROCESO):
                objeto.estado = self.PROCESADO
                objeto.save()
                contador += 1
        if contador == 0:
            self.message_user(request, "No se proceso ninguna remision, verificar estado")
        if contador == 1:
            self.message_user(request, "Se proceso %s nota de remision" %contador)
        if contador > 1:
            self.message_user(request, "Se procesaron %s notas de remision" %contador)
        url = reverse('admin:app_notaremision_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    procesar.short_description = "Actualizar Estado A Procesado"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:notaremision_id>)/', self.admin_site.admin_view(self.procesar_remision), name='remision_enviar'),
            path('imprimir/<int:notaremision_id>', self.admin_site.admin_view(self.imprimir_remision), name='remision_imprimir'),]
            #path('imprimir/<int:notaremision_id>', app.reports.nota_remision_report, name='remision_imprimir'),]
        return custom_urls + urls

    def accion_remision(self, obj):
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" target="_blank" href="{}">Imprimir</a>',
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
                lastObject = self.get_max_object(request, NotaRemision, 'nroRemision')
                remision.nroRemision = int(lastObject.nroRemision+1) if lastObject else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                remision.save()
            else:
                self.message_user(request, "Remision Ya Procesada")
        url = reverse('admin:app_notaremision_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    
    #metodo para imprimir el pedido
    def imprimir_remision(self, request, notaremision_id, *args, **kwargs):
        remision = self.get_object(request, notaremision_id)
        if (remision and remision.estado != self.BORRADOR):
            return app.reports.nota_remision_report(request, notaremision_id)
        else:
            url = reverse('admin:app_notaremision_changelist',current_app=request.resolver_match.namespace)
            return HttpResponseRedirect(url)

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs) 
        if (not obj and form.base_fields):
            if not (form.base_fields['nroRemision'].initial):
                form.base_fields['nroRemision'].initial = 0
                form.base_fields['nroRemision'].disabled = True
        return form

    def generar_recepcion(self, request, queryset):
        contador = 0
        for remision in queryset:
            try:
                recepcion = Recepcion()
                recepcion.fecha = timezone.localtime(timezone.now())
                recepcion.nroRecepcion = 0
                recepcion.remision = remision
                recepcion.departamentoOrigen = remision.departamentoDestino
                recepcion.departamentoDestino = remision.departamentoOrigen 
                recepcion.estado = self.BORRADOR
                recepcion.usuario = request.user
                recepcion.save()
                for inline in remision.notaremisiondetalle_set.all():
                    detalle = RecepcionDetalle()
                    detalle.recepcion = recepcion
                    detalle.cantidad = inline.cantidad
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.save()
                contador+=1
                NotaRemision.objects.filter(nroRemision=remision.nroRemision).update(estado=self.PROCESADO,fecha=timezone.localtime(timezone.now()))
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
    fields = ('recepcion','articulo','cantidad','unidadMedida')
    extra = 2

class RecepcionAdmin(Nota):
    inlines = (RecepcionInLine,)
    list_display = ('nroRecepcion','fecha','departamentoOrigen','departamentoDestino','estado','accion_recepcion')
    fields = ('fecha','usuario','nroRecepcion','remision','departamentoOrigen','departamentoDestino','estado')
    read_only_fields = ('fecha','estado',)
    ordering = ['nroRecepcion']
    list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']
    actions = ['procesar']

    def procesar(self, request, queryset):
        contador = 0
        for objeto in queryset:
            if (objeto.estado != self.PROCESADO):
                objeto.estado = self.PROCESADO
                lastObject = self.get_max_object(request, Recepcion, 'nroRecepcion')
                objeto.nroRecepcion = int(lastObject.nroRecepcion+1) if lastObject else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                objeto.fecha = timezone.localtime(timezone.now())
                objeto.save()
                contador += 1
        if contador == 0:
            self.message_user(request, "No se proceso ninguna recepcion, verificar estado")
        if contador == 1:
            self.message_user(request, "Se proceso %s recepcion" %contador)
        if contador > 1:
            self.message_user(request, "Se procesaron %s recepciones" %contador)
        url = reverse('admin:app_recepcion_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    procesar.short_description = "Actualizar Estado A Procesado"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:recepcion_id>)/', self.admin_site.admin_view(self.confirmar_recepcion), name='recepcion_confirmar'),
            path('imprimir/<int:recepcion_id>/', self.admin_site.admin_view(self.imprimir_recepcion), name='recepcion_imprimir'),]
            #path('imprimir/<int:recepcion_id>', app.reports.recepcion_report, name='recepcion_imprimir'),]
        return custom_urls + urls

    def accion_recepcion(self, obj):
        return format_html('<a class="button" href="{}">Confirmar</a>&nbsp;'
            '<a class="button" href="{}" target="_blank">Imprimir</a>',
            reverse('admin:recepcion_confirmar', args=[obj.pk]),
            reverse('admin:recepcion_imprimir', args=[obj.pk]),)
    accion_recepcion.short_description = 'Procesar'
    accion_recepcion.allow_tags = True

    def confirmar_recepcion(self, request, recepcion_id, *args, **kwargs):
        recepcion = self.get_object(request, recepcion_id)
        if (recepcion):
            if (recepcion.estado == self.BORRADOR):
                recepcion.estado = self.PROCESADO
                lastObject = self.get_max_object(request, Recepcion, 'nroRecepcion')
                recepcion.nroRecepcion = int(lastObject.nroRecepcion+1) if lastObject else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                recepcion.fecha = timezone.localtime(timezone.now())
                recepcion.save()
            else:
                self.message_user(request, "Recepcion Ya Procesada")
        url = reverse('admin:app_recepcion_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    #metodo para imprimir el pedido
    def imprimir_recepcion(self, request, recepcion_id, *args, **kwargs):
        recepcion = self.get_object(request, recepcion_id)
        if (recepcion and recepcion.estado != self.BORRADOR):
            return app.reports.recepcion_report(request, recepcion_id)
        else:
            url = reverse('admin:app_recepcion_changelist',current_app=request.resolver_match.namespace)
            return HttpResponseRedirect(url)

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if (not obj and form.base_fields):
            if not (form.base_fields['nroRecepcion'].initial):
                form.base_fields['nroRecepcion'].initial = 0
                form.base_fields['nroRecepcion'].disabled = True
            #if (form.base_fields['remision'].initial):
            #    form.base_fields['remision'].widget = HiddenInput()
        return form

class SolicitudPresupuestoInLine(admin.TabularInline):
    model = SolicitudPresupuestoDetalle
    can_delete = True
    verbore_name_plural = 'Artículos'
    fields = ('solicitudPresupuesto','articulo','descripcion','cantidad','unidadMedida','precio','subtotal')
    readonly_fields = ('subtotal',)
    

class SolicitudPresupuestoAdmin(admin.ModelAdmin):
        
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    PROCESADO = 'P'
    READ_ONLY = False

    inlines = (SolicitudPresupuestoInLine,)
    list_display = ('nroPresupuesto','fecha','fechaEntrega','proveedor','estado','accion_presupuesto')
    fields = ('fecha','usuario','nroPresupuesto','pedido','proveedor','fechaEntrega','terminosCondiciones','plazoPago','moneda','total','estado')
    read_only_fields = ('fecha','estado',)
    ordering = ['nroPresupuesto']
    #list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if (not obj and form.base_fields):
            if not (form.base_fields['nroPresupuesto'].initial):
                form.base_fields['nroPresupuesto'].initial = 0
                form.base_fields['nroPresupuesto'].disabled = True
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
        form.base_fields['usuario'].widget = HiddenInput()
        form.base_fields['total'].widget = HiddenInput()
        form.base_fields['estado'].widget = HiddenInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:solicitudpresupuesto_id>)/', self.admin_site.admin_view(self.confirmar_presupuesto), name='presupuesto_confirmar'),
            path('imprimir/(<int:solicitudpresupuesto_id>)/', self.admin_site.admin_view(self.imprimir_presupuesto), name='presupuesto_imprimir'),]
        return custom_urls + urls

    def accion_presupuesto(self, obj):
        return format_html('<a class="button" href="{}">Confirmar</a>&nbsp;'
            '<a class="button" href="{}" target="_blank">Imprimir</a>',
            reverse('admin:presupuesto_confirmar', args=[obj.pk]),
            reverse('admin:presupuesto_imprimir', args=[obj.pk]),)
    accion_presupuesto.short_description = 'Procesar'
    accion_presupuesto.allow_tags = True

    def confirmar_presupuesto(self, request, presupuesto_id, *args, **kwargs):
        #recepcion = self.get_object(request, recepcion_id)
        #if (recepcion):
        #    if (recepcion.estado == self.BORRADOR):
        #        recepcion.estado = self.PROCESADO
        #        lastObject = self.get_max_object(request, Recepcion, 'nroRecepcion')
        #        recepcion.nroRecepcion = int(lastObject.nroRecepcion+1) if lastObject else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
        #        recepcion.fecha = timezone.localtime(timezone.now())
        #        recepcion.save()
        #    else:
        #        self.message_user(request, "Recepcion Ya Procesada")
        url = reverse('admin:app_solicitudpresupuesto_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    #metodo para imprimir el pedido
    def imprimir_presupuesto(self, request, presupuesto_id, *args, **kwargs):
        #recepcion = self.get_object(request, recepcion_id)
        #if (recepcion and recepcion.estado != self.BORRADOR):
        #    return app.reports.recepcion_report(request, recepcion_id)
        #else:
        url = reverse('admin:app_solicitudpresupuesto_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        objecto = self.get_object(request, object_id)
        self.READ_ONLY = False
        if (objecto and objecto.estado != self.BORRADOR):
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
                inline.can_delete = False
                inline.max_num = 0
        else:
            self.readonly_fields = ('fecha',) #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = ('subtotal',)#inline.get_readonly_fields(inline, request)
                inline.can_delete = True
                inline.max_num = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        if self.READ_ONLY:
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context = None):
        self.READ_ONLY = False
        self.readonly_fields = ('fecha',)
        for inline in self.inlines:
            inline.readonly_fields = []
            inline.can_delete = True
            inline.max_num = None
        return super().changelist_view(request, extra_context)

class OrdenCompraInLine(admin.TabularInline):
    model = OrdenCompraDetalle
    can_delete = True
    verbore_name_plural = 'Artículos'
    

class OrdenCompraAdmin(admin.ModelAdmin):
    inlines = (OrdenCompraInLine,)

    class Media:
        js = ("app/scripts/admin.js",)

class FacturaCompraInLine(admin.TabularInline):
    model = FacturaCompraDetalle
    can_delete = True
    verbore_name_plural = 'Artículos'
    

class FacturaCompraAdmin(admin.ModelAdmin):
    inlines = (FacturaCompraInLine,)

    class Media:
        js = ("app/scripts/admin.js",)

class UsuarioInLine(admin.TabularInline):
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
admin.site.register(SolicitudPresupuesto, SolicitudPresupuestoAdmin)
admin.site.register(OrdenCompra, OrdenCompraAdmin)
admin.site.register(FacturaCompra, FacturaCompraAdmin)
admin.site.register(Articulo)
admin.site.register(Proveedor)
admin.site.register(Departamento)
admin.site.register(Sucursal)
admin.site.register(DepartamentoSucursal)
admin.site.register(TipoArticulo)
admin.site.register(CategoriaArticulo)
admin.site.register(UnidadMedida)
admin.site.register(Moneda)
admin.site.register(PlazoPago)