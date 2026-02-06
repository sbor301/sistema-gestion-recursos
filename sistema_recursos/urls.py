"""
URL configuration for sistema_recursos project.
"""
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('proyectos.urls')), 
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

# Personalización del Admin Panel 
admin.site.site_header = "Administración RMS"
admin.site.site_title = "Portal RRHH"
admin.site.index_title = "Bienvenido al Sistema de Gestión"
admin.site.site_url = "/"