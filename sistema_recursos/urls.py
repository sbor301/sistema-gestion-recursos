"""
URL configuration for sistema_recursos project.
"""
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Esta es la ÚNICA línea necesaria para tu app.
    # Dice: "Cualquier cosa que llegue (incluso vacía), mándala a proyectos.urls"
    path('', include('proyectos.urls')), 
]

# Personalización del Admin Panel (Esto déjalo, está perfecto)
admin.site.site_header = "Administración RMS"
admin.site.site_title = "Portal RRHH"
admin.site.index_title = "Bienvenido al Sistema de Gestión"
admin.site.site_url = "/"