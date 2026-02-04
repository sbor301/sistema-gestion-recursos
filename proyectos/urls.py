from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Pantallas Principales
    path('', views.index, name='index'), 
    path('gantt/', views.vista_gantt, name='gantt'),
    path('buscar/', views.buscar_disponibilidad, name='buscar'),
    path('recursos/', views.ver_recursos, name='recursos'),
    path('proyectos-lista/', views.lista_proyectos, name='lista_proyectos'),
    path('reporte/', views.reporte_recurso, name='reporte_recurso'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/admin/'), name='logout'),
    
    # Funcionalidades / API 
    path('api/actualizar_tarea/', views.actualizar_tarea_api, name='actualizar_tarea_api'),
    path('asignar/<int:tarea_id>/<int:recurso_id>/', views.asignar_recurso, name='asignar_recurso'),
]