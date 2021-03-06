# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Image, Spacer, TableStyle  
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm,inch,mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table
from datetime import datetime
from reportlab.pdfgen import canvas
from PresupuestosWeb import settings
from app.models import *
from django.conf.locale import *
import locale
locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')



def nota_pedido_report(request,id):
    
    master = NotaPedido.objects.get(id=id)
    detail = master.notapedidodetalle_set.all()
    cant_elementos = len(detail)

    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    #Header
    c.setTitle("Nota Pedido")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220,790,'NOTA DE PEDIDO')
    c.drawString(250, 770,'Nº')
    nro = c.drawString(270, 770, str(master.nroPedido))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    #imagen = Image(archivo_imagen, width=50, height=50,hAlign='LEFT')
    c.drawString(400, 780,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 770, width=70, height=45)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["BodyText"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 12
    
    
    #parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 8,fontName="Times-Roman")
    
    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Para: ")
    c.drawString(270, 740, "De: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 740, str(master.departamentoDestino))
    c.drawString(295, 740, str(master.departamentoOrigen))
    c.drawString(80, 720, "Solicitamos nos provean de los siguientes: ")

    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    elements.append(headings)
    elements.append(results)
    #c.setFont("Times-Roman", 6)
    
    
    #Detalle Tabla
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    #elements.append(table)
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 29*mm, (242*mm)-(cant_elementos*mm*5.2))
    

    #table.wrapOn(c, 800, 600)
    #if cant_elementos < 5:
    #    table.drawOn(c, 80, y-58)
    #else:
    #    table.drawOn(c, 80, 400)

    c.setFont("Times-Bold", 12)
    c.drawString(80, 480, "Para uso en: ")
    c.drawString(80, 460, "Precio aproximado: ")
    c.setFont("Times-Roman", 12)
    c.drawString(190, 480, to_str(master.descripcionUso))
    c.drawString(190, 460, to_str(master.precioAproximado))

    c.line(80, 435, 220, 435)
    c.line(270, 435, 350, 435)
    c.line(410, 435, 500, 435)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 420, "Vo.Bo. Gte. Administrativo")
    c.drawString(280, 420, "Jefe de Est.")
    c.drawString(415, 420, "Gerente de Área")

    #Header2
    #c.setLineWidth(.3)
    #c.setFont("Times-Roman", 12)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220,380,'NOTA DE PEDIDO')
    c.drawString(250, 360,'Nº')
    nro = c.drawString(270, 360, str(master.nroPedido))
    c.drawString(400, 380,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 360, width=70, height=45)

    c.drawString(80, 340,  "Para: ")
    c.drawString(280, 340, "De: " )
    c.setFont("Times-Roman", 12)
    c.drawString(110, 340, str(master.departamentoDestino))
    c.drawString(300, 340, str(master.departamentoOrigen))
    c.drawString(80, 320, "Solicitamos nos provean de los siguientes: ")

    #Detalle Tabla 2
    table2 = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table2.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    #elements.append(table2)
    table2.wrapOn(c, width, height)
    table2.drawOn(c, 29*mm, (100*mm)-(cant_elementos*mm*5.2))
   

    c.setFont("Times-Bold", 12)
    c.drawString(80, 70, "Para uso en: ")
    c.drawString(80, 50, "Precio aproximado: ")
    c.setFont("Times-Roman", 12)
    c.drawString(190, 70, to_str(master.descripcionUso))
    c.drawString(190, 50, to_str(master.precioAproximado))
    #elements.append(Paragraph(c.drawString(80, 55, "Precio aproximado: " + to_str(master.precioAproximado)) ,parrafoStyle))

    c.line(80, 30, 220, 30)
    c.line(270, 30, 350, 30)
    c.line(410, 30, 500, 30)
    
    c.setFont("Times-Roman", 8)
    c.drawString(85, 15, "Vo.Bo. Gte. Administrativo")
    c.drawString(280, 15, "Jefe de Est.")
    c.drawString(415, 15, "Gerente de Área")
    
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


    

def nota_remision_report(request, id):

    master = NotaRemision.objects.get(id=id)
    detail = master.notaremisiondetalle_set.all()
    cant_elementos = len(detail)
    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_remision.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    #Header
    c.setTitle("Nota Remision")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220,790,'NOTA DE REMISIÓN')
    c.drawString(250, 770,'Nº')
    nro = c.drawString(270, 770, str(master.nroRemision))
    c.drawString(400, 790,  master.fecha.strftime('%d-%m-%Y'))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    c.drawImage(archivo_imagen, 80, 760, width=70, height=45)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 8
    
    
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]


    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Para: ")
    c.drawString(80, 720, "De: ")
    c.drawString(80, 700, "Ref.: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 740, str(master.departamentoDestino))
    c.drawString(110, 720, str(master.departamentoOrigen))
    c.drawString(110, 700, str(master.pedido))
    c.drawString(80, 680, "Para los fines consiguientes estamos entregando los siguientes insumos para la Estación: ")

    elements.append(headings)
    elements.append(results)

    #Detalle Tabla
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, width, height)
    table.drawOn(c, 29*mm, (230*mm)-(cant_elementos*mm*5.2))

    c.line(80, 440, 220, 440)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 430, str(master.departamentoOrigen))

    #Header2
    #c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220, 390,'NOTA DE REMISIÓN')
    c.drawString(250, 375,'Nº')
    nro = c.drawString(270, 375, str(master.nroRemision))
    c.drawString(400, 390,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 370, width=70, height=45)

    c.drawString(80, 350, "Para: ")
    c.drawString(80, 330, "De: ")
    c.drawString(80, 310, "Ref.: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 350, str(master.departamentoDestino))
    c.drawString(110, 330, str(master.departamentoOrigen))
    c.drawString(110, 310, str(master.pedido))
    c.drawString(80, 290, "Para los fines consiguientes estamos entregando los siguientes insumos para la Estación: ")

    #Detalle Tabla 2
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, width, height)
    table.drawOn(c, 29*mm, (92*mm)-(cant_elementos*mm*5.2))

    c.line(80, 35, 220, 35)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 25, str(master.departamentoOrigen))


    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


    


def recepcion_report(request, id):

    master = Recepcion.objects.get(id=id)
    detail = master.recepciondetalle_set.all()
    response = HttpResponse(content_type = 'application/pdf')
    cant_elementos = len(detail)
    #pdf_name = "nota_recepcion.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    #Header
    c.setTitle("Nota Recepcion")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    c.drawString(200,790, 'NOTA DE RECEPCIÓN')
    c.drawString(250, 770, 'Nº')
    nro = c.drawString(270, 770, str(master.nroRecepcion))
    c.drawString(400, 790, master.fecha.strftime('%d-%m-%Y'))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    c.drawImage(archivo_imagen, 80, 760, width=70, height=45)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 8
    
    
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Para: ")
    c.drawString(80, 720, "De: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 740, str(master.departamentoDestino))
    c.drawString(110, 720, str(master.departamentoOrigen))
    
    elements.append(headings)
    elements.append(results)

    #Detalle Tabla
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, width, height)
    table.drawOn(c, 29*mm, (243*mm)-(cant_elementos*mm*5.2))

    c.setFont("Times-Roman", 8)
    c.line(80, 450, 210, 450)
    c.drawString(85, 440, str(master.departamentoOrigen))

    #Header2
    #c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    c.drawString(200, 390,'NOTA DE RECEPCIÓN')
    c.drawString(250, 375,'Nº')
    nro = c.drawString(270, 375, str(master.nroRecepcion))
    c.drawString(400, 390,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 370, width=70, height=45)

    c.drawString(80, 350, "Para: ")
    c.drawString(80, 330, "De: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 350, str(master.departamentoDestino))
    c.drawString(110, 330, str(master.departamentoOrigen))


    #Detalle Tabla 2
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch], rowHeights=0.2*inch,splitByRow=10)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'BOTTOM'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, width, height)
    table.drawOn(c, 29*mm, (104*mm)-(cant_elementos*mm*5.2))

    c.line(80, 45, 210, 45)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 30, str(master.departamentoOrigen))

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

  


def presupuesto_report(request, id):

    master = SolicitudPresupuesto.objects.get(id=id)
    detail = master.solicitudpresupuestodetalle_set.all()
    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_recepcion.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setTitle("Solicitud Presupuesto")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(200,790, 'SOLICITUD PRESUPUESTO')
    nro = c.drawString(250, 770, 'Nº ' + str(master.nroPresupuesto))
    c.drawString(400, 790, master.fecha.strftime('%d-%m-%Y'))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    c.drawImage(archivo_imagen, 80, 760, width=65, height=50)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["BodyText"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10
    
    
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 8,fontName="Times-Roman")
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción', 'Precio', 'Subtotal')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion, formatMoneda(d.precio), formatMoneda(d.subtotal)) for d in detail]
    #elements.append(tabla_encabezado(styles,titulo1,nro))
    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Proveedor: ")
    c.drawString(80, 720, "Fecha Entrega: ")
    c.drawString(350, 720, "Moneda: ")
    c.drawString(80, 240, "Total: ")
    c.drawString(80, 220, "Forma de Pago: ")
    c.drawString(200, 220, "Términos y Condiciones: " )
    c.drawString(80, 180, "Ref. Pedido: ")
    c.drawString(80, 160, "Usuario: ")
    
    c.setFont("Times-Roman", 12)
    c.drawString(165, 740, str(master.proveedor))
    c.drawString(165, 720, str(master.fechaEntrega))
    c.drawString(400, 720, str(master.moneda))
    #c.drawString(480, 240, '{:,}'.format(master.total) )
    c.drawString(480, 240, str(formatMoneda(master.total)))
    c.drawString(80, 200, str(master.plazoPago))
    c.drawString(330, 220, str(master.terminosCondiciones))
    c.drawString(150, 180, str(master.pedido))
    c.drawString(150, 160, str(master.usuario))
    
    elements.append(headings)
    elements.append(results)

    #Detalle Tabla
    table = Table([headings]+results, colWidths=[0.7*inch, 1.22*inch, 3.0*inch,0.8*inch,0.8*inch],rowHeights=0.18*inch)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'MIDDLE'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 600, 500)
    table.drawOn(c, 80, 660)

    
    c.setFont("Times-Roman", 8)
    c.line(80, 70, 160, 70)
    c.line(250, 70, 340, 70)
    c.line(400, 70, 480, 70)
    c.drawString(90, 55, "Gerente de Área")
    c.drawString(280, 55, "Hecho por")
    c.drawString(430, 55, "Vº Bº")

    

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def ocompra_report(request, id):

    master = OrdenCompra.objects.get(id=id)
    detail = master.ordencompradetalle_set.all()
    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_recepcion.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setTitle("Orden Compra")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    c.drawString(200,790, 'ORDEN COMPRA')
    c.drawString(250, 770, 'Nº')
    nro = c.drawString(270, 770, str(master.nroOrdenCompra))
    c.drawString(400, 790, master.fecha.strftime('%d-%m-%Y'))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    c.drawImage(archivo_imagen, 80, 760, width=70, height=45)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 8
    
    
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 8,fontName="Times-Roman")
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción', 'Precio', 'Subtotal')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion, formatMoneda(d.precio), formatMoneda(d.subtotal)) for d in detail]
    #elements.append(tabla_encabezado(styles,titulo1,nro))
    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Proveedor: ")
    c.drawString(80, 720, "Fecha Entrega: ")
    c.drawString(350, 720, "Moneda: ")
    c.drawString(80, 240, "Total: ")
    c.drawString(80, 220, "Forma de Pago: ")
    c.drawString(200, 220, "Términos y Condiciones: " )
    c.drawString(80, 180, "Ref. Pedido: ")
    c.drawString(80, 160, "Usuario: ")
    
    c.setFont("Times-Roman", 12)
    c.drawString(165, 740, str(master.proveedor))
    c.drawString(165, 720, str(master.fechaEntrega))
    c.drawString(400, 720, str(master.moneda))
    #c.drawString(480, 240, '{:,}'.format(master.total))
    c.drawString(480, 240, str(formatMoneda(master.total)) )
    c.drawString(80, 200, str(master.plazoPago))
    c.drawString(330, 220, str(master.terminosCondiciones))
    c.drawString(150, 180, str(master.pedido))
    c.drawString(150, 160, str(master.usuario))
    
    elements.append(headings)
    elements.append(results)

    #Detalle Tabla
    table = Table([headings]+results, colWidths=[0.7*inch, 1.22*inch, 3.0*inch,0.8*inch,0.8*inch],rowHeights=0.18*inch)
    table.setStyle(TableStyle(
                        [
                            ('VALIGN', (0,0), (- 1, -1), 'MIDDLE'),
                            ('GRID', (0, 0), (4, -3), 1, colors.black),
                            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                            ('ALIGN', (4,0), (-1,-1), 'CENTER'),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 600, 500)
    table.drawOn(c, 80, 660)

    
    c.setFont("Times-Roman", 8)
    c.line(80, 70, 160, 70)
    c.line(250, 70, 340, 70)
    c.line(400, 70, 480, 70)
    c.drawString(90, 55, "Gerente de Área")
    c.drawString(280, 55, "Hecho por")
    c.drawString(430, 55, "Vº Bº")

    
    

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response



def getDoc(buff, title):
    return SimpleDocTemplate(buff,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=20,
                            bottomMargin=18,
                            title=title
                            )

def cabecera(canvas, texto, numero):
    #setLineWidth(.3)
    #setFont("Times-Bold", 12)
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    #imagen = Image(archivo_imagen, width=50, height=50,hAlign='LEFT')
    #imagen = drawImage(archivo_imagen, 80, 760, width=70, height=45)
    #canvas.drawImage(archivo_imagen, 80, 760, width=70, height=45)


def tabla_encabezado(styles,texto,numero):
        sp = ParagraphStyle('parrafos',alignment = TA_CENTER,fontSize = 16, fontName="Times-Roman")
        try:
            #print(settings.STATIC_ROOT)
            archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
            imagen = Image(archivo_imagen, width=50, height=50,hAlign='LEFT')
        except:
            raise
            imagen = Paragraph(u"LOGO", sp)
        
        #nota = Paragraph(u"NOTA DE PEDIDO", sp)
        nota = Paragraph(texto, sp)
        id_movimiento = Paragraph('N° ' + numero, sp)
        fecha = Paragraph("FECHA: "+datetime.today().strftime('%d/%m/%y'), sp)        
        encabezado = [ [imagen,nota,fecha], ['',id_movimiento,''] ]
        tabla_encabezado = Table(encabezado,colWidths=[4 * cm, 9 * cm, 6 * cm])
        tabla_encabezado.setStyle(TableStyle(
            [
                ('VALIGN',(0,0),(2,0),'CENTER'),
                ('VALIGN',(1,1),(2,1),'TOP'),                
                ('SPAN',(0,0),(0,1)),                        
            ]
        ))
        
        return tabla_encabezado
      
def to_str(s):
    if s is None:
        return ''
    return str(s)

def formatMoneda(n):
    return locale.format("%.0f", n, grouping=True)

