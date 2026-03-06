from django.contrib import admin
from .models import Proyecto, Tarea, Cliente, Asistencia # <-- Agregamos Asistencia

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
    
    # NUEVO: Protegemos la llave secreta para que nadie la modifique por error
    readonly_fields = ('llave_asistencia',)

# 3. Configuración del Admin de TAREAS 
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
    
    # --- PRE-LLENAR DATOS DESDE URL ---
    def get_changeform_initial_data(self, request):
        """
        Pre-llena el formulario con datos que vienen por la URL (GET).
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
                # Convertir en una lista de enteros 
                skill_ids = [int(s) for s in skills_str.split(',') if s.isdigit()]
                initial['requisitos'] = skill_ids
            except ValueError:
                pass # Si hay basura en la URL, se ignora

        return initial

# 4. NUEVO: Configuración del Admin de ASISTENCIAS
@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('recurso', 'proyecto', 'tipo_registro', 'fecha_hora', 'metodo_validacion')
    list_filter = ('proyecto', 'tipo_registro', 'metodo_validacion')
    search_fields = ('recurso__nombre', 'proyecto__nombre')
    date_hierarchy = 'fecha_hora' # Calendario navegable en la parte superior