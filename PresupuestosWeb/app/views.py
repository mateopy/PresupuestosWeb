﻿"""
Definition of views.
"""
from app.models import *
from app.forms import *
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.core.serializers.json import DjangoJSONEncoder
from app.functions import *
from app.reports import *
from django.http import JsonResponse
import json


def reporte_nota_pedido(request,id):
    return nota_pedido_report(request,id)



#NOTA DE PEDIDO
def pedidos(request):
            
    pedidos = NotaPedido.objects.filter()    
    
    return render(request, 'app/pedidos/lista.html', 
                  {'title': 'Pedidos',
                   'usuarios':usuarios, 
                   })

def pedidos_detalle(request,id='0'):
    mensaje = mensajeError = ''
    
    instance = get_object_or_404(NotaPedido, id=id)
    form = PedidoForm(instance=instance)

    return render(request, 'app/pedidos/detalle.html', 
      {'title': 'Detalle Pedido', 'form': form, })


def pedidos_nuevo(request):
    mensaje = ''
    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "¡La Nota de pedido ha sido creada con éxito!"
            form = PedidoForm()
    else:
        form = PedidoForm()   
    
    
    return render(request, 'app/pedidos/nuevo.html', 
        {'title': 'Nuevo Pedido', 'form': form, 'mensaje': mensaje,})


def pedidos_editar(request,id):
    mensaje = mensajeError = ''
    
    if request.method == "POST":
        instance = get_object_or_404(NotaPedido, id=id)
        form = PedidoForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            mensaje = "¡El pedido ha sido modificado!"
                
                       
    elif request.method == "GET":
        instance = NotaPedido.objects.filter(estado=='B',id=id).first()
        if instance:
            form = PedidoForm(instance=instance)
        else:
            raise Http404  
    
    
    
    return render(request, 'app/pedidos/editar.html', {'title': 'Editar Pedido', 'form': form, 'mensaje': mensaje, 'mensajeError':mensajeError})


def pedidos_eliminar(request,id):
    mensaje = mensajeError = ''
    
    if request.method == "POST":
        instance = get_object_or_404(NotaPedido, id=id)
        form = PedidoForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            mensaje = "¡El pedido ha sido modificado!"
                
                       
    elif request.method == "GET":
        instance = NotaPedido.objects.filter(estado=='B',id=id).first()
        if instance:
            form = PedidoForm(instance=instance)
        else:
            raise Http404  
    
    
    
    return render(request, 'app/pedidos/editar.html', {'title': 'Editar Pedido', 'form': form, 'mensaje': mensaje, 'mensajeError':mensajeError})


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

#@login_required
def get_articulo(request):
    id = request.GET.get('id_articulo',None)
    data = {}
    if id:
        articulo = Articulo.objects.get(pk=id)
        if articulo:
            data.update({
                'descripcion':articulo.descripcion
                })
    return JsonResponse(data)

@csrf_exempt 
def login_usuarios(request):

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
                
        user = authenticate(username=username, password=password)
    
        if user is not None:
            if user.is_active:
                permissions = get_user_permissions(user)
                #qs_json = serializers.serialize('json', permissions)
                #qs_json = serializers.serialize('json', list(permissions))
                qs_json = json.dumps(list(permissions), cls=DjangoJSONEncoder)
                return JsonResponse(qs_json,status=200,safe=False)
                #return JsonResponse({'results': list(permissions)})
            else:
                JsonResponse({'error':'Usuario Inactivo'},status=400)
        else:
            return JsonResponse({'error':'Usuario o Contraseña no válida'},status=401)

def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.values_list('codename')
    return user.user_permissions.values_list('codename').all() | Permission.objects.values_list('codename').filter(group__user=user)