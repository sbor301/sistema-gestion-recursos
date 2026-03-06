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
    path('importar/', views.centro_importacion, name='centro_importacion'),
    path('importar/recursos/', views.importar_recursos_excel, name='importar_recursos_excel'),
    path('importar/plantilla-recursos/', views.descargar_plantilla_recursos, name='descargar_plantilla_recursos'),
    path('importar/proyectos/', views.importar_proyectos_excel, name='importar_proyectos_excel'),
    path('importar/plantilla-proyectos/', views.descargar_plantilla_proyectos, name='descargar_plantilla_proyectos'),
    path('reportes/clientes/', views.reporte_cliente, name='reporte_cliente'),
    path('talento/buscar/', views.buscador_talento, name='buscador_talento'),
    path('talento/exportar/excel/', views.exportar_excel_talento, name='exportar_talento_excel'),
    path('talento/exportar/pdf/', views.exportar_pdf_talento, name='exportar_talento_pdf'),
    path('proyecto/<int:proyecto_id>/asistencia/panel/', views.panel_supervisor_qr, name='panel_supervisor_qr'),
    path('api/proyecto/<int:proyecto_id>/codigo-actual/', views.api_codigo_actual, name='api_codigo_actual'),
    path('proyecto/<int:proyecto_id>/asistencia/registro/', views.registro_asistencia_operario, name='registro_asistencia_operario'),
    path('asistencia/', views.portal_asistencia, name='portal_asistencia'),

    
    
    # Funcionalidades / API 
    path('api/actualizar_tarea/', views.actualizar_tarea_api, name='actualizar_tarea_api'),
    path('asignar/<int:tarea_id>/<int:recurso_id>/', views.asignar_recurso, name='asignar_recurso'),
]