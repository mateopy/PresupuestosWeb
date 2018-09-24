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
from .views import get_articulo
urlpatterns = [
    # Uncomment the next line to enable the admin:
    url(r'^get_articulo',get_articulo ),
 
]
