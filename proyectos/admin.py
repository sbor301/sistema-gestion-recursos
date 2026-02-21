from django.contrib import admin
from .models import Proyecto, Tarea, Cliente

# 1. Configuración del Admin de CLIENTES
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto_principal', 'email_contacto')
    search_fields = ('nombre',)

# 2. Configuración del Admin de PROYECTOS
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_negocio', 'centro_costo', 'fecha_inicio', 'fecha_fin_estimada')
    
    # Edición rápida desde la lista
    list_editable = ('unidad_negocio', 'centro_costo') 
    
    list_filter = ('unidad_negocio', 'centro_costo')
    search_fields = ('nombre', 'centro_costo')

# 3. Configuración del Admin de TAREAS (Todo unificado aquí)
@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    # A. Visualización
    list_display = ('nombre', 'ver_unidad_negocio', 'ver_centro_costo', 'proyecto', 'asignado_a', 'fecha_inicio', 'fecha_fin', 'progreso')
    
    # B. Filtros laterales
    list_filter = ('proyecto__unidad_negocio', 'proyecto__centro_costo', 'asignado_a')
    
    # C. Buscador
    search_fields = ('nombre', 'proyecto__centro_costo')
    
    # D. Edición rápida
    list_editable = ('fecha_inicio', 'fecha_fin', 'progreso')

    # E. Selector de habilidades (Cajita doble)
    filter_horizontal = ('requisitos',)

    # --- MÉTODOS VISUALES ---
    @admin.display(description='Unidad de Negocio')
    def ver_unidad_negocio(self, obj):
        return obj.proyecto.unidad_negocio

    @admin.display(description='Centro de Costo')
    def ver_centro_costo(self, obj):
        return obj.proyecto.centro_costo
    
    # --- MÉTODO MÁGICO PARA PRE-LLENAR DATOS DESDE URL ---
    def get_changeform_initial_data(self, request):
        """
        Pre-llena el formulario con datos que vienen por la URL (GET).
        Útil para el botón 'Asignar Tarea' del buscador de talento.
        """
        initial = super().get_changeform_initial_data(request)
        
        # 1. Capturar el usuario asignado (si viene en la URL)
        asignado_id = request.GET.get('asignado_a')
        if asignado_id:
            initial['asignado_a'] = asignado_id

        # 2. Capturar las skills (si vienen en la URL)
        skills_str = request.GET.get('skills')
        if skills_str:
            try:
                # Convertimos "1,4,8" en una lista de enteros [1, 4, 8]
                skill_ids = [int(s) for s in skills_str.split(',') if s.isdigit()]
                initial['requisitos'] = skill_ids
            except ValueError:
                pass # Si hay basura en la URL, la ignoramos

        return initial