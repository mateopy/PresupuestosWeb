# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Image, Spacer  
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import cm,inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import Table
from datetime import datetime
from django.contrib.auth.models import User
import os
from PresupuestosWeb import settings
from app.models import *


def nota_pedido_report(request,id):
    
    master = NotaPedido.objects.get(id=id)
    detail = master.notapedidodetalle_set.all()
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    titulo1 = "NOTA DE PEDIDO"
    nro = str(id)


    response = HttpResponse(content_type='application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = getDoc(buff,'Nota de Pedido')
    elements = []
    styles = getSampleStyleSheet()
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    
    #ENCABEZADO
    elements.append(tabla_encabezado(styles,titulo1,nro))
    #header = Paragraph("Listado de Usuarios", styles['Heading1'])
    #elements.append(header)
    
    #CABECERA
    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("<b>Para: </b>" + str(master.departamentoDestino),parrafoStyle))
    elements.append(Paragraph("<b>De: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentoSucursal),parrafoStyle))
    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("Solicitamos nos provean de los siguientes: ",parrafoStyle))
    elements.append(Spacer(2,0.2*inch))
    
    #DETALLE
    table = Table([headings] + results)
    table.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.transparent),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))
    elements.append(table)

    #PIE
    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("Para uso en: " + to_str(master.descripcionUso),parrafoStyle))
    elements.append(Paragraph("Precio Aproximado: " + to_str(master.precioAproximado) ,parrafoStyle))


    doc.build(elements)
    response.write(buff.getvalue())
    buff.close()
    return response

def nota_remision_report(request, id):

    master = NotaRemision.objects.get(id=id)
    detail = master.notaremisiondetalle_set.all()
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    titulo1 = "NOTA DE REMISION"
    nro = str(id)


    response = HttpResponse(content_type='application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = getDoc(buff,'Nota de Remisión')
    elements = []
    styles = getSampleStyleSheet()
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    
    #ENCABEZADO
    elements.append(tabla_encabezado(styles,titulo1,nro))
    #header = Paragraph("Listado de Usuarios", styles['Heading1'])
    #elements.append(header)
    
    #CABECERA
    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("<b>Nota de Pedido: </b>" + str(master.pedido),parrafoStyle))
    elements.append(Paragraph("<b>Para: </b>" + str(master.departamentoDestino),parrafoStyle))
    elements.append(Paragraph("<b>De: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentoSucursal),parrafoStyle))
    elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Pedidos proveidos: ",parrafoStyle))
    elements.append(Spacer(2,0.2*inch))
    
    #DETALLE
    table = Table([headings] + results)
    table.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.transparent),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))
    elements.append(table)

    #PIE
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Para uso en: " + to_str(master.descripcionUso),parrafoStyle))
    #elements.append(Paragraph("Precio Aproximado: " + to_str(master.precioAproximado) ,parrafoStyle))


    doc.build(elements)
    response.write(buff.getvalue())
    buff.close()
    return response

def recepcion_report(request, id):

    master = Recepcion.objects.get(id=id)
    detail = master.recepciondetalle_set.all()
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    titulo1 = "RECEPCIÓN"
    nro = str(id)


    response = HttpResponse(content_type='application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = getDoc(buff,'Recepción')
    elements = []
    styles = getSampleStyleSheet()
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    
    #ENCABEZADO
    elements.append(tabla_encabezado(styles,titulo1,nro))
    #header = Paragraph("Listado de Usuarios", styles['Heading1'])
    #elements.append(header)
    
    #CABECERA
    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("<b>Nota de Remisión: </b>" + str(master.remision),parrafoStyle))
    elements.append(Paragraph("<b>Para: </b>" + str(master.departamentoDestino),parrafoStyle))
    elements.append(Paragraph("<b>De: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentoSucursal),parrafoStyle))
    elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Pedidos proveidos: ",parrafoStyle))
    elements.append(Spacer(2,0.2*inch))
    
    #DETALLE
    table = Table([headings] + results)
    table.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.transparent),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))
    elements.append(table)

    #PIE
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Para uso en: " + to_str(master.descripcionUso),parrafoStyle))
    #elements.append(Paragraph("Precio Aproximado: " + to_str(master.precioAproximado) ,parrafoStyle))


    doc.build(elements)
    response.write(buff.getvalue())
    buff.close()
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

def tabla_encabezado(styles,texto,numero):
        sp = ParagraphStyle('parrafos',alignment = TA_CENTER,fontSize = 16, fontName="Times-Roman")
        try:
            print(settings.STATIC_ROOT)
            archivo_imagen = settings.STATIC_ROOT+'/images/logo.png'
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