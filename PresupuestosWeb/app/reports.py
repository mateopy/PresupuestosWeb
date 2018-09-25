# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Image, Spacer, TableStyle  
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm,inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table
from datetime import datetime
from reportlab.pdfgen import canvas
from PresupuestosWeb import settings
from app.models import *



def nota_pedido_report(request,id):
    
    master = NotaPedido.objects.get(id=id)
    detail = master.notapedidodetalle_set.all()

    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setTitle("Nota Pedido")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220,790,'NOTA DE PEDIDO')
    c.drawString(250, 770,'Nº')
    nro = c.drawString(270, 770, str(id))
    print(settings.STATIC_ROOT)
    archivo_imagen = settings.STATIC_ROOT+'/app/images/logo.png'
    #imagen = Image(archivo_imagen, width=50, height=50,hAlign='LEFT')
    c.drawString(400, 780,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 770, width=70, height=45)

    #Table Header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 12
    
    
    parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    
    c.setFont("Times-Bold", 12)
    c.drawString(80, 740, "Para: ")
    c.drawString(80, 720, "De: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 740, str(master.departamentoDestino))
    c.drawString(110, 720, str(master.departamentoOrigen))
    c.drawString(80, 700, "Solicitamos nos provean de los siguientes: ")

    elements.append(headings)
    elements.append(results)

    #Detalle Tabla
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 600, 500)
    table.drawOn(c, 80, 630)

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
    nro = c.drawString(270, 360, str(id))
    c.drawString(400, 380,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 360, width=70, height=45)
    c.drawString(80, 340,  "Para: ")
    c.drawString(80, 320, "De: " )
    c.setFont("Times-Roman", 12)
    c.drawString(110, 340, str(master.departamentoDestino))
    c.drawString(110, 320, str(master.departamentoOrigen))
    c.drawString(80, 300, "Solicitamos nos provean de los siguientes: ")

    #Detalle Tabla 2
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 250, 150)
    table.drawOn(c, 80, 230)
    c.setFont("Times-Bold", 12)
    c.drawString(80, 90, "Para uso en: ")
    c.drawString(80, 70, "Precio aproximado: ")
    c.setFont("Times-Roman", 12)
    c.drawString(190, 90, to_str(master.descripcionUso))
    c.drawString(190, 70, to_str(master.precioAproximado))
    #elements.append(Paragraph(c.drawString(80, 55, "Precio aproximado: " + to_str(master.precioAproximado)) ,parrafoStyle))

    c.line(80, 45, 220, 45)
    c.line(270, 45, 350, 45)
    c.line(410, 45, 500, 45)
    
    c.setFont("Times-Roman", 8)
    c.drawString(85, 30, "Vo.Bo. Gte. Administrativo")
    c.drawString(280, 30, "Jefe de Est.")
    c.drawString(415, 30, "Gerente de Área")
    
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


    #headings = ('cantidad', 'unidad de medida', 'descripción')
    #results = [(d.cantidad, d.unidadmedida, d.articulo.descripcion) for d in detail]
    ###t=table(results,2*[0.4*inch], 3*[0.4*inch])

    #titulo1 = "nota de pedido"
    #nro = str(id)


    #response = httpresponse(content_type='application/pdf')
    ###pdf_name = "nota_pedido.pdf" 
    ### response['content-disposition'] = 'attachment; filename=%s' % pdf_name
    #buff = bytesio()
    #doc = getdoc(buff,'nota de pedido')
    #elements = []
    #styles = getsamplestylesheet()
    #parrafostyle = paragraphstyle('parrafos',alignment = ta_justify,fontsize = 12,fontname="times-roman")
    
    ###encabezado
    #elements.append(tabla_encabezado(styles,titulo1,nro))
    ###header = paragraph("listado de usuarios", styles['heading1'])
    ###elements.append(header)
    
    ###cabecera
    #elements.append(spacer(1,0.2*inch))
    #elements.append(paragraph("<b>para: </b>" + str(master.departamentodestino),parrafostyle))
    #elements.append(spacer(1,0.2*inch))
    #elements.append(paragraph("<b>de: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentosucursal),parrafostyle))
    #elements.append(spacer(1,0.2*inch))
    #elements.append(paragraph("solicitamos nos provean de los siguientes: ",parrafostyle))
    #elements.append(spacer(2,0.2*inch))
    
    ###detalle
    #table = table([headings] + results,colwidths=[1.35*inch, 1.35*inch, 3.5*inch], rowheights=0.25*inch)
 
    #table.setstyle(tablestyle(
    #    [
    #        ('grid', (0, 0), (4, -3), 1, colors.black),
    #        ('innergrid', (0, 0), (-1, -1), 1, colors.black),
    #        ('box', (0, 0), (-1, -1), 1, colors.black),
    #        ('linebelow', (0, 0), (-1, 0), 1, colors.black),
    #        ('background', (0, 0), (-1, 0), colors.transparent)
    #    ]
    #))
    #elements.append(table)
    #elements.append(spacer(1,2*inch))

    ###pie
    #elements.append(spacer(1,0.2*inch))
    #elements.append(paragraph("para uso en: " + to_str(master.descripcionuso),parrafostyle))
    #elements.append(spacer(1,0.2*inch))
    #elements.append(paragraph("precio aproximado: " + to_str(master.precioaproximado) ,parrafostyle))


    #doc.build(elements)
    #response.write(buff.getvalue())
    #buff.close()
    #return response

    #Fin Original
    

def nota_remision_report(request, id):

    master = NotaRemision.objects.get(id=id)
    detail = master.notaremisiondetalle_set.all()

    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_remision.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setTitle("Nota Remision")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220,790,'NOTA DE REMISIÓN')
    c.drawString(250, 770,'Nº')
    nro = c.drawString(270, 770, str(id))
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
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 600, 500)
    table.drawOn(c, 80, 600)

    c.line(80, 440, 220, 440)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 430, str(master.departamentoOrigen))

    #Header2
    #c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    titulo1 = c.drawString(220, 390,'NOTA DE REMISIÓN')
    c.drawString(250, 375,'Nº')
    nro = c.drawString(270, 375, str(id))
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
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 250, 200)
    table.drawOn(c, 80, 210)

    c.line(80, 35, 220, 35)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 25, str(master.departamentoOrigen))


    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

    #headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    #results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    #titulo1 = "NOTA DE REMISION"
    #nro = str(id)


    #response = HttpResponse(content_type='application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    #buff = BytesIO()
    #doc = getDoc(buff,'Nota de Remisión')
    #elements = []
    #styles = getSampleStyleSheet()
    #parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    
    #ENCABEZADO
    #elements.append(tabla_encabezado(styles,titulo1,nro))
    #header = Paragraph("Listado de Usuarios", styles['Heading1'])
    #elements.append(header)
    
    #CABECERA
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("<b>Nota de Pedido: </b>" + str(master.pedido),parrafoStyle))
    #elements.append(Paragraph("<b>Para: </b>" + str(master.departamentoDestino),parrafoStyle))
    #elements.append(Paragraph("<b>De: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentoSucursal),parrafoStyle))
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Pedidos proveidos: ",parrafoStyle))
    #elements.append(Spacer(2,0.2*inch))
    
    #DETALLE
    #table = Table([headings] + results)
    #table.setStyle(TableStyle(
    #    [
    #        ('GRID', (0, 0), (3, -1), 1, colors.transparent),
    #        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
    #        ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
    #    ]
    #))
    #elements.append(table)

    #PIE
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Para uso en: " + to_str(master.descripcionUso),parrafoStyle))
    #elements.append(Paragraph("Precio Aproximado: " + to_str(master.precioAproximado) ,parrafoStyle))


    #doc.build(elements)
    #response.write(buff.getvalue())
    #buff.close()
    #return response

    


def recepcion_report(request, id):

    master = Recepcion.objects.get(id=id)
    detail = master.recepciondetalle_set.all()
    response = HttpResponse(content_type = 'application/pdf')
    #pdf_name = "nota_recepcion.pdf" 
    #response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    elements = []
    buffer = BytesIO()
    #doc = getDoc(buff,'nota de pedido')
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setTitle("Nota Recepcion")
    c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    c.drawString(200,790, 'NOTA DE RECEPCIÓN')
    c.drawString(250, 770, 'Nº')
    nro = c.drawString(270, 770, str(id))
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
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 600, 500)
    table.drawOn(c, 80, 620)

    c.setFont("Times-Roman", 8)
    c.line(80, 450, 210, 450)
    c.drawString(85, 440, str(master.departamentoOrigen))

    #Header2
    #c.setLineWidth(.3)
    c.setFont("Times-Bold", 12)
    c.drawString(200, 390,'NOTA DE RECEPCIÓN')
    c.drawString(250, 375,'Nº')
    nro = c.drawString(270, 375, str(id))
    c.drawString(400, 390,  master.fecha.strftime('%d-%m-%Y'))
    c.drawImage(archivo_imagen, 80, 370, width=70, height=45)

    c.drawString(80, 350, "Para: ")
    c.drawString(80, 330, "De: ")
    c.setFont("Times-Roman", 12)
    c.drawString(110, 350, str(master.departamentoDestino))
    c.drawString(110, 330, str(master.departamentoOrigen))


    #Detalle Tabla 2
    table = Table([headings]+results, colWidths=[1.35*inch, 1.35*inch, 3.5*inch])
    table.setStyle(TableStyle(
                        [ ('GRID', (0, 0), (4, -3), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                        ]
                    ))

    elements.append(table)
    table.wrapOn(c, 250, 150)
    table.drawOn(c, 80, 225)

    c.line(80, 45, 210, 45)
    c.setFont("Times-Roman", 8)
    c.drawString(85, 30, str(master.departamentoOrigen))

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

    #headings = ('Cantidad', 'Unidad de Medida', 'Descripción')
    #results = [(d.cantidad, d.unidadMedida, d.articulo.descripcion) for d in detail]
    #titulo1 = "RECEPCIÓN"
    #nro = str(id)


    #response = HttpResponse(content_type='application/pdf')
    #pdf_name = "nota_pedido.pdf" 
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    #buff = BytesIO()
    #doc = getDoc(buff,'Recepción')
    #elements = []
    #styles = getSampleStyleSheet()
    #parrafoStyle = ParagraphStyle('parrafos',alignment = TA_JUSTIFY,fontSize = 12,fontName="Times-Roman")
    
    #ENCABEZADO
    #elements.append(tabla_encabezado(styles,titulo1,nro))
    #header = Paragraph("Listado de Usuarios", styles['Heading1'])
    #elements.append(header)
    
    #CABECERA
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("<b>Nota de Remisión: </b>" + str(master.remision),parrafoStyle))
    #elements.append(Paragraph("<b>Para: </b>" + str(master.departamentoDestino),parrafoStyle))
    #elements.append(Paragraph("<b>De: </b>" + str(master.usuario.get_full_name) + " - " + str(master.usuario.usuario.departamentoSucursal),parrafoStyle))
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Pedidos proveidos: ",parrafoStyle))
    #elements.append(Spacer(2,0.2*inch))
    
    #DETALLE
    #table = Table([headings] + results)
    #table.setStyle(TableStyle(
    #    [
    #        ('GRID', (0, 0), (3, -1), 1, colors.black),
    #        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
    #        ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
    #    ]
    #))
    #elements.append(table)

    #PIE
    #elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph("Para uso en: " + to_str(master.descripcionUso),parrafoStyle))
    #elements.append(Paragraph("Precio Aproximado: " + to_str(master.precioAproximado) ,parrafoStyle))


    #doc.build(elements)
    #response.write(buff.getvalue())
    #buff.close()
    #return response


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