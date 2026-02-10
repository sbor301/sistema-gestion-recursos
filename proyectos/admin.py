from django.contrib import admin
from .models import Proyecto, Tarea

# 1. Configuración del Admin de PROYECTOS
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    # 1. Columnas que se ven
    list_display = ('nombre', 'unidad_negocio', 'centro_costo', 'fecha_inicio', 'fecha_fin_estimada')
    
    list_editable = ('unidad_negocio', 'centro_costo') 
    
    list_filter = ('unidad_negocio', 'centro_costo')
    search_fields = ('nombre', 'centro_costo')

# 2. Configuración del Admin de TAREAS
@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    # A. LIST_DISPLAY: funciones para traer el dato del Proyecto
    list_display = ('nombre', 'ver_unidad_negocio', 'ver_centro_costo', 'proyecto', 'asignado_a', 'fecha_inicio', 'fecha_fin', 'progreso')
    
    # B. LIST_FILTER
 
    list_filter = ('proyecto__unidad_negocio', 'proyecto__centro_costo', 'asignado_a')
    
    # C. SEARCH_FIELDS: buscar por el CC del proyecto
    search_fields = ('nombre', 'proyecto__centro_costo')
    
    list_editable = ('fecha_inicio', 'fecha_fin', 'progreso')

    # Esto crea el selector de doble cuadro (Izquierda: Disponibles | Derecha: Seleccionados)
    filter_horizontal = ('requisitos',)

    # D. DEFINICIÓN DE LAS FUNCIONES PARA VER DATOS DEL PADRE
    @admin.display(description='Unidad de Negocio')
    def ver_unidad_negocio(self, obj):
        # "obj" es la Tarea. 
        return obj.proyecto.unidad_negocio

    @admin.display(description='Centro de Costo')
    def ver_centro_costo(self, obj):
        return obj.proyecto.centro_costo