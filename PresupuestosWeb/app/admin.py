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
    PENDIENTE_APROBACION = 'PA'
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
    verbose_name_plural = 'Detalle'
    #fields = ('notaPedido','cantidad','unidadMedida','articulo')
    fields = ('notaPedido','articulo','cantidad','unidadMedida')
    extra = 2

class NotaPedidoPresupuestoInLine(admin.TabularInline):
    model = NotaPedidoPresupuesto
    fields = ('presupuesto','observaciones')
    can_delete = True
    verbose_name_plural = 'Presupuestos'
    extra = 1

class NotaPedidoAdmin(Nota):
    #readonly_fields = ('fechaCreacion','fechaActualizacion')
    inlines = (NotaPedidoInLine,NotaPedidoPresupuestoInLine)
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
            self.message_user(request, "No se procesó ningún pedido, verificar estado")
        if contador == 1:
            self.message_user(request, "Se procesó %s nota de pedido" %contador)
        if contador > 1:
            self.message_user(request, "Se procesaron %s notas de pedidos" %contador)
        url = reverse('admin:app_notapedido_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)
    procesar.short_description = "Actualizar Estado A Procesado"

    def generar_presupuesto(self, request, queryset):
        contador = 0
        for pedido in queryset:
            try:
                presupuesto = SolicitudPresupuesto()
                presupuesto.fecha = timezone.localtime(timezone.now())
                presupuesto.nroPresupuesto = 0
                presupuesto.pedido = pedido
                presupuesto.estado = self.BORRADOR
                presupuesto.usuario = request.user
                presupuesto.save()
                for inline in pedido.notapedidodetalle_set.all():
                    detalle = SolicitudPresupuestoDetalle()
                    detalle.solicitudPresupuesto = presupuesto
                    detalle.cantidad = inline.cantidad
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.save()
                contador+=1
                #OrdenCompra.objects.filter(nro=pedido.nroPedido).update(estado=self.PROCESADO,fecha=timezone.localtime(timezone.now()))
            except Exception as e:
                #self.message_user(request, str(e))
                self.message_user(request, "Ocurrio un error durante la generacion, verificar pedidos")
        if contador == 1:
            mensaje = "1 Presupuesto Generado"
        else:
            mensaje = "%s Presupuestos Generados " % contador
        self.message_user(request,"%s Satisfactoriamente" % mensaje)
    generar_presupuesto.short_description = "Generar Presupuesto/s"

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

        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Enviar</a>&nbsp;', 
                                     reverse('admin:pedido_enviar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:pedido_imprimir', args=[obj.pk]),)

        if (objeto and (objeto.estado == self.BORRADOR)): 
            botones = botonConfirmar
        if (objeto and (objeto.estado == self.PROCESADO or objeto.estado == self.EN_PROCESO or objeto.estado == self.PENDIENTE_APROBACION)): 
            botones = botonImprimir

        a = botones         
        
        return a
        
        """
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" target="_blank" href="{}">Imprimir</a>',
            reverse('admin:pedido_enviar', args=[obj.pk]),
            reverse('admin:pedido_imprimir', args=[obj.pk]),)
        """
    accion_pedido.short_description = 'Procesar'
    accion_pedido.allow_tags = True

    #metodo para cambiar procesar los pedidos
    def enviar_pedido(self, request, notapedido_id, *args, **kwargs):
        pedido = self.get_object(request, notapedido_id)
        if (pedido):
            if (pedido.estado == self.BORRADOR):
                pedido.estado = self.PENDIENTE_APROBACION
                lastObject = self.get_max_object(request, NotaPedido, 'nroPedido')
                pedido.nroPedido = int(lastObject.nroPedido+1) if lastObject.nroPedido != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
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
        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Enviar</a>&nbsp;', 
                                     reverse('admin:remision_enviar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:remision_imprimir', args=[obj.pk]),)

        if (objeto and (objeto.estado == self.BORRADOR)): 
            botones = botonConfirmar
        if (objeto and (objeto.estado == self.PROCESADO or objeto.estado == self.EN_PROCESO)): 
            botones = botonImprimir

        a = botones         
        
        return a
        """
        return format_html('<a class="button" href="{}">Enviar</a>&nbsp;'
            '<a class="button" target="_blank" href="{}">Imprimir</a>',
            reverse('admin:remision_enviar', args=[obj.pk]),
            reverse('admin:remision_imprimir', args=[obj.pk]),)
        """
    accion_remision.short_description = 'Procesar'
    accion_remision.allow_tags = True

    #metodo para cambiar procesar los pedidos
    def procesar_remision(self, request, notaremision_id, *args, **kwargs):
        remision = self.get_object(request, notaremision_id)
        if (remision):
            if (remision.estado == self.BORRADOR):
                remision.estado = self.EN_PROCESO
                lastObject = self.get_max_object(request, NotaRemision, 'nroRemision')
                remision.nroRemision = int(lastObject.nroRemision+1) if lastObject.nroRemision != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
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
                objeto.nroRecepcion = int(lastObject.nroRecepcion+1) if lastObject.nroRecepcion != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
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
        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Confirmar</a>&nbsp;', 
                                     reverse('admin:recepcion_confirmar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:recepcion_imprimir', args=[obj.pk]),)

        if (objeto and (objeto.estado == self.BORRADOR)): 
            botones = botonConfirmar
        if (objeto and (objeto.estado == self.PROCESADO or objeto.estado == self.EN_PROCESO)): 
            botones = botonImprimir

        a = botones         
        
        return a
        """
        return format_html('<a class="button" href="{}">Confirmar</a>&nbsp;'
            '<a class="button" href="{}" target="_blank">Imprimir</a>',
            reverse('admin:recepcion_confirmar', args=[obj.pk]),
            reverse('admin:recepcion_imprimir', args=[obj.pk]),)
        """
    accion_recepcion.short_description = 'Procesar'
    accion_recepcion.allow_tags = True

    def confirmar_recepcion(self, request, recepcion_id, *args, **kwargs):
        recepcion = self.get_object(request, recepcion_id)
        if (recepcion):
            if (recepcion.estado == self.BORRADOR):
                recepcion.estado = self.PROCESADO
                lastObject = self.get_max_object(request, Recepcion, 'nroRecepcion')
                if not lastObject: 
                    recepcion.nroRecepcion = int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                else:
                    recepcion.nroRecepcion = int(lastObject.nroRecepcion+1) if lastObject.nroRecepcion != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
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
    #readonly_fields = ('subtotal',)

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
    actions = ('generar_orden_compra',)
    #list_filter = ['fecha','departamentoOrigen','departamentoDestino','estado']

    class Media:
        js = ("app/scripts/admin.js",)

    def generar_orden_compra(self, request, queryset):
        contador = 0
        for presupuesto in queryset:
            try:
                compra = OrdenCompra()
                compra.fecha = timezone.localtime(timezone.now())
                compra.nroOrdenCompra = 0
                compra.pedido = presupuesto.pedido
                compra.proveedor = presupuesto.proveedor
                compra.fechaEntrega = presupuesto.fechaEntrega
                compra.terminosCondiciones = presupuesto.terminosCondiciones
                compra.plazoPago = presupuesto.plazoPago
                compra.moneda = presupuesto.moneda
                compra.total = presupuesto.total
                compra.estado = self.BORRADOR
                compra.usuario = request.user
                compra.save()
                for inline in presupuesto.solicitudpresupuestodetalle_set.all():
                    detalle = OrdenCompraDetalle()
                    detalle.notaCompra = compra
                    detalle.cantidad = inline.cantidad
                    detalle.precio = inline.precio
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.descripcion = inline.descripcion
                    detalle.subtotal = inline.subtotal
                    detalle.moneda = compra.moneda
                    detalle.save()
                contador+=1
                SolicitudPresupuesto.objects.filter(nroPresupuesto=presupuesto.nroPresupuesto).update(estado=self.PROCESADO,fecha=timezone.localtime(timezone.now()))
            except Exception as e:
                #self.message_user(request, str(e))
                self.message_user(request, "Ocurrio un error durante la generacion, verificar presupuestos")
        if contador == 1:
            mensaje = "1 Orden de Compra Generada"
        else:
            mensaje = "%s Ordenes de Compra Generadas " % contador
        self.message_user(request,"%s Satisfactoriamente" % mensaje)
    generar_orden_compra.short_description = "Generar Orden/es de Compra"


    def save_formset(self, request, form, formset, change):
        inlines = formset.save(commit=False)
        for inline in inlines:
            inline.moneda = self.objeto.moneda
            inline.save()
        self.save_model(request, self.objeto, form, change)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        total = 0.0
        if obj:
            for inline in obj.solicitudpresupuestodetalle_set.all():
                total += inline.subtotal
            obj.total = total
            obj.save()
        self.objeto = obj

    
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
            path('procesar/(<int:presupuesto_id>)/', self.admin_site.admin_view(self.confirmar_presupuesto), name='presupuesto_confirmar'),
            path('imprimir/<int:presupuesto_id>/', self.admin_site.admin_view(self.imprimir_presupuesto), name='presupuesto_imprimir'),]
        return custom_urls + urls

    def accion_presupuesto(self, obj):
        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Confirmar</a>&nbsp;', 
                                     reverse('admin:presupuesto_confirmar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:presupuesto_imprimir', args=[obj.pk]),)

        if (objeto and objeto.estado == self.BORRADOR): 
            botones = botonConfirmar
        if (objeto and objeto.estado == self.PROCESADO): 
            botones = botonImprimir

        a = botones         
        
        return a

    accion_presupuesto.short_description = 'Procesar'
    accion_presupuesto.allow_tags = True

    def confirmar_presupuesto(self, request, presupuesto_id, *args, **kwargs):
      
        presupuesto = self.get_object(request, presupuesto_id)
        if (presupuesto):
            if (presupuesto.estado == self.BORRADOR):
                presupuesto.estado = self.PROCESADO
                lastObject = self.get_max_object(request, SolicitudPresupuesto , 'nroPresupuesto')
                presupuesto.nroPresupuesto = int(lastObject.nroPresupuesto+1) if lastObject.nroPresupuesto != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                presupuesto.fecha = timezone.localtime(timezone.now())
                presupuesto.save()
            else:
                self.message_user(request, "Presupuesto Ya Procesado")
        url = reverse('admin:app_solicitudpresupuesto_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def get_max_object(self, request, modelo, campo):
        #qpedido = NotaPedido.objects.annotate(Max('nroPedido')).filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal)
        try:
            lastObjeto = modelo.objects.filter().latest(campo)
        except:
            lastObjeto = None

        return lastObjeto

    #metodo para imprimir el pedido
    def imprimir_presupuesto(self, request, presupuesto_id, *args, **kwargs):
        #recepcion = self.get_object(request, recepcion_id)
        #if (recepcion and recepcion.estado != self.BORRADOR):
        #    return app.reports.recepcion_report(request, recepcion_id)
        #else:
        presupuesto = self.get_object(request, presupuesto_id)

        if (presupuesto and presupuesto.estado != self.BORRADOR):
            return app.reports.presupuesto_report(request, presupuesto_id)
        else: 
            url = reverse('admin:app_solicitudpresupuesto_changelist',current_app=request.resolver_match.namespace)
            return HttpResponseRedirect(url)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        objecto = self.get_object(request, object_id)
        self.READ_ONLY = False
        if (objecto and objecto.estado != self.BORRADOR):
            self.READ_ONLY = True
            extra_context = extra_context or {}
            #extra_context['show_save_and_continue'] = False
            #extra_context['show_delete'] = False
            #extra_context['show_save'] = False
            #extra_context['show_save_and_add_another'] = False
            variables = []
            for field in self.get_fields(request):
                variables.append(field)
            self.readonly_fields = tuple(variables)

            for inline in self.inlines:
                #inline.readonly_fields = tuple(inline.get_fields(inline, request))
                inline.readonly_fields = ('solicitudPresupuesto','articulo','descripcion','unidadMedida')
                #inline.can_delete = False
                inline.max_num = 0
        else:
            self.readonly_fields = ('fecha',) #self.get_readonly_fields(request)
            for inline in self.inlines:
                #inline.readonly_fields = ('subtotal',)#inline.get_readonly_fields(inline, request)
                #inline.can_delete = True
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
    fields = ('notaCompra','articulo','descripcion','cantidad','unidadMedida','precio','subtotal')

class OrdenCompraAdmin(admin.ModelAdmin):
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    PROCESADO = 'P'
    READ_ONLY = False

    inlines = (OrdenCompraInLine,)
    list_display = ('nroOrdenCompra','fecha','fechaEntrega','proveedor','estado','accion_compra')
    fields = ('fecha','usuario','nroOrdenCompra','pedido','proveedor','fechaEntrega','terminosCondiciones','plazoPago','moneda','total','estado')
    read_only_fields = ('fecha','estado',)
    ordering = ['nroOrdenCompra']
    actions = ('generar_factura_compra',)

    class Media:
        js = ("app/scripts/admin.js",)

    def generar_factura_compra(self, request, queryset):
        contador = 0
        for compra in queryset:
            try:
                factura = FacturaCompra()
                factura.fecha = timezone.localtime(timezone.now())
                factura.nroFacturaCompra = 0
                factura.ordenCompra = compra
                factura.pedido = compra.pedido
                factura.proveedor = compra.proveedor
                factura.fechaEntrega = compra.fechaEntrega
                factura.terminosCondiciones = compra.terminosCondiciones
                factura.plazoPago = compra.plazoPago
                factura.moneda = compra.moneda
                factura.total = compra.total
                factura.estado = self.BORRADOR
                factura.usuario = request.user
                factura.save()
                for inline in compra.ordencompradetalle_set.all():
                    detalle = FacturaCompraDetalle()
                    detalle.facturaCompra = factura
                    detalle.cantidad = inline.cantidad
                    detalle.precio = inline.precio
                    detalle.unidadMedida = inline.unidadMedida
                    detalle.articulo = inline.articulo
                    detalle.descripcion = inline.descripcion
                    detalle.subtotal = inline.subtotal
                    detalle.moneda = compra.moneda
                    detalle.save()
                contador+=1
                #OrdenCompra.objects.filter(nroOrdenCompra=compra.nroOrdenCompra).update(estado=self.PROCESADO,fecha=timezone.localtime(timezone.now()))
            except Exception as e:
                #self.message_user(request, str(e))
                self.message_user(request, "Ocurrio un error durante la generacion, verificar ordenes")
        if contador == 1:
            mensaje = "1 Factura de Compra Generada"
        else:
            mensaje = "%s Facturas de Compra Generadas " % contador
        self.message_user(request,"%s Satisfactoriamente" % mensaje)
    generar_factura_compra.short_description = "Generar Factura/s de Compra"


    def save_formset(self, request, form, formset, change):
        inlines = formset.save(commit=False)
        for inline in inlines:
            inline.moneda = self.objeto.moneda
            inline.save()
        self.save_model(request, self.objeto, form, change)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        total = 0.0
        if obj:
            for inline in obj.ordencompradetalle_set.all():
                total += inline.subtotal
            obj.total = total
            obj.save()
        self.objeto = obj

    
    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if (not obj and form.base_fields):
            if not (form.base_fields['nroOrdenCompra'].initial):
                form.base_fields['nroOrdenCompra'].initial = 0
                form.base_fields['nroOrdenCompra'].disabled = True
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
            form.base_fields['usuario'].widget = HiddenInput()
            form.base_fields['total'].widget = HiddenInput()
            form.base_fields['estado'].widget = HiddenInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:orden_compra_id>)/', self.admin_site.admin_view(self.confirmar_orden_compra), name='orden_compra_confirmar'),
            path('imprimir/<int:orden_compra_id>/', self.admin_site.admin_view(self.imprimir_orden_compra), name='orden_compra_imprimir'),]
        return custom_urls + urls

    def accion_compra(self, obj):
        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Confirmar</a>&nbsp;', 
                                     reverse('admin:orden_compra_confirmar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:orden_compra_imprimir', args=[obj.pk]),)

        if (objeto and objeto.estado == self.BORRADOR): 
            botones = botonConfirmar
        if (objeto and objeto.estado == self.PROCESADO): 
            botones = botonImprimir

        a = botones         
        
        return a

    accion_compra.short_description = 'Procesar'
    accion_compra.allow_tags = True

    def confirmar_orden_compra(self, request, orden_compra_id, *args, **kwargs):
      
        compra = self.get_object(request, orden_compra_id)
        if (compra):
            if (compra.estado == self.BORRADOR):
                compra.estado = self.PROCESADO
                lastObject = self.get_max_object(request, OrdenCompra , 'nroOrdenCompra')
                compra.nroOrdenCompra = int(lastObject.nroOrdenCompra+1) if lastObject.nroOrdenCompra != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                compra.fecha = timezone.localtime(timezone.now())
                compra.save()
            else:
                self.message_user(request, "Orden de Compra Ya Procesada")
        url = reverse('admin:app_ordencompra_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def get_max_object(self, request, modelo, campo):
        #qpedido = NotaPedido.objects.annotate(Max('nroPedido')).filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal)
        try:
            lastObjeto = modelo.objects.filter().latest(campo)
        except:
            lastObjeto = None

        return lastObjeto

    def imprimir_orden_compra(self, request, orden_compra_id, *args, **kwargs):
        compra = self.get_object(request, orden_compra_id)

        if (compra and compra.estado != self.BORRADOR):
            return app.reports.ocompra_report(request, orden_compra_id)
        else:
            url = reverse('admin:app_ordencompra_changelist',current_app=request.resolver_match.namespace)
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
                #inline.readonly_fields = ('solicitudPresupuesto','articulo','descripcion','unidadMedida')
                inline.can_delete = False
                inline.max_num = 0
        else:
            self.readonly_fields = ('fecha',) #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = []
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

class FacturaCompraInLine(admin.TabularInline):
    model = FacturaCompraDetalle
    can_delete = True
    verbore_name_plural = 'Artículos'
    fields = ('facturaCompra','articulo','descripcion','cantidad','unidadMedida','precio','subtotal')
    
class FacturaCompraAdmin(admin.ModelAdmin):
    BORRADOR = 'B'
    EN_PROCESO = 'E'
    PROCESADO = 'P'
    READ_ONLY = False

    inlines = (FacturaCompraInLine,)

    class Media:
        js = ("app/scripts/admin.js",)

    list_display = ('nroFacturaCompra','fecha','ordenCompra','proveedor','estado','accion_compra')
    fields = ('fecha','usuario','nroFacturaCompra','pedido','proveedor','ordenCompra','plazoPago','moneda','total','estado')
    read_only_fields = ('fecha','estado',)
    ordering = ['nroFacturaCompra']

    def save_formset(self, request, form, formset, change):
        inlines = formset.save(commit=False)
        for inline in inlines:
            inline.moneda = self.objeto.moneda
            inline.save()
        self.save_model(request, self.objeto, form, change)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        total = 0.0
        if obj:
            for inline in obj.facturacompradetalle_set.all():
                total += inline.subtotal
            obj.total = total
            obj.save()
        self.objeto = obj

    
    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if (not obj and form.base_fields):
            if not (form.base_fields['nroFacturaCompra'].initial):
                form.base_fields['nroFacturaCompra'].initial = 0
                form.base_fields['nroFacturaCompra'].disabled = True
            if not (form.base_fields['usuario'].initial):
                form.base_fields['usuario'].initial = request.user
            form.base_fields['usuario'].widget = HiddenInput()
            form.base_fields['total'].widget = HiddenInput()
            form.base_fields['estado'].widget = HiddenInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [#url(r'^$', app.views.home, name='home')
            path('procesar/(<int:factura_compra_id>)/', self.admin_site.admin_view(self.confirmar_factura_compra), name='factura_compra_confirmar'),
            path('imprimir/<int:factura_compra_id>/', self.admin_site.admin_view(self.imprimir_factura_compra), name='factura_compra_imprimir'),]
        return custom_urls + urls

    def accion_compra(self, obj):
        objeto = obj
        botonConfirmar = format_html('<a class="button" href="{}">Confirmar</a>&nbsp;', 
                                     reverse('admin:factura_compra_confirmar', args=[obj.pk]),)
        botonImprimir = format_html('<a class="button" href="{}" target="_blank">Imprimir</a>', 
                                    reverse('admin:factura_compra_imprimir', args=[obj.pk]),)

        if (objeto and objeto.estado == self.BORRADOR): 
            botones = botonConfirmar
        if (objeto and objeto.estado == self.PROCESADO): 
            botones = botonImprimir

        a = botones         
        
        return a

    accion_compra.short_description = 'Procesar'
    accion_compra.allow_tags = True

    def confirmar_factura_compra(self, request, factura_compra_id, *args, **kwargs):
      
        compra = self.get_object(request, factura_compra_id)
        if (compra):
            if (compra.estado == self.BORRADOR):
                compra.estado = self.PROCESADO
                lastObject = self.get_max_object(request, FacturaCompra , 'nroFacturaCompra')
                compra.nroFacturaCompra = int(lastObject.nroFacturaCompra+1) if lastObject.nroFacturaCompra != 0 else int(request.user.usuario.departamentoSucursal.sucursal.codigo)*10000+1
                compra.fecha = timezone.localtime(timezone.now())
                compra.save()
            else:
                self.message_user(request, "Factura de Compra Ya Procesada")
        url = reverse('admin:app_facturacompra_changelist',current_app=request.resolver_match.namespace)
        return HttpResponseRedirect(url)

    def get_max_object(self, request, modelo, campo):
        #qpedido = NotaPedido.objects.annotate(Max('nroPedido')).filter(departamentoOrigen__sucursal=request.user.usuario.departamentoSucursal.sucursal)
        try:
            lastObjeto = modelo.objects.filter().latest(campo)
        except:
            lastObjeto = None

        return lastObjeto

    def imprimir_factura_compra(self, request, factura_compra_id, *args, **kwargs):
        compra = self.get_object(request, factura_compra_id)

        #if (compra and compra.estado != self.BORRADOR):
        #    return app.reports.presupuesto_report(request, presupuesto_id)
        #else: 
        url = reverse('admin:app_facturacompra_changelist',current_app=request.resolver_match.namespace)
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
                #inline.readonly_fields = ('solicitudPresupuesto','articulo','descripcion','unidadMedida')
                inline.can_delete = False
                inline.max_num = 0
        else:
            self.readonly_fields = ('fecha',) #self.get_readonly_fields(request)
            for inline in self.inlines:
                inline.readonly_fields = []
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

class UsuarioInLine(admin.TabularInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Perfiles'

class UsuarioAdmin(UserAdmin):
    inlines = (UsuarioInLine,)


class AutorizadorInLine(admin.TabularInline):
    model = DepartamentoSucursalAutorizador
    can_delete = True
    extra = 1
    verbose_name_plural = 'Autorizadores'

class DepartamentoSucursalAdmin(admin.ModelAdmin):
    inlines = (AutorizadorInLine,)
    


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
admin.site.register(DepartamentoSucursal,DepartamentoSucursalAdmin)
admin.site.register(TipoArticulo)
admin.site.register(CategoriaArticulo)
admin.site.register(UnidadMedida)
admin.site.register(Moneda)
admin.site.register(PlazoPago)