"""
Definition of urls for PresupuestosWeb.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    #NOTA DE PEDIDO
    url(r'^pedidos/$', app.views.pedidos, name='pedidos'),
    url(r'^pedidos/detalle/(?P<id>\S+)$', app.views.pedidos_detalle, name='pedidos_detalle'),
    url(r'^pedidos/nuevo/$', app.views.pedidos_nuevo, name='pedidos_nuevo'),
    url(r'^pedidos/editar/(?P<id>\S+)$', app.views.pedidos_editar, name='pedidos_editar'),
    url(r'^pedidos/eliminar/(?P<id>\S+)$', app.views.pedidos_eliminar, name='pedidos_eliminar'),

    # Examples:
    #url(r'^$', app.views.home, name='home'),
    
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about', app.views.about, name='about'),
    url(r'^administracion/app/notapedido/imprimir/(?P<id>\S+)$', app.views.reporte_nota_pedido, name='reporte_nota_pedido'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^administracion/', admin.site.urls),
    url(r'^$', admin.site.urls),
]
