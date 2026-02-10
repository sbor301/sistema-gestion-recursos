from django.contrib import admin
from .models import Perfil, Recurso, Conocimiento, Habilidad

# 1. Registro simple de Perfiles (Ingeniero, Técnico, etc.)
admin.site.register(Perfil)

# 2. Configuración del Catálogo de Conocimientos (PLC, Redes, etc.)
@admin.register(Conocimiento)
class ConocimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    search_fields = ('nombre', 'categoria') # Vital para que funcione el autocompletado

# 3. Configuración de la "Tabla Interna" 
# Esto hace que las habilidades aparezcan DENTRO del empleado
class HabilidadInline(admin.TabularInline):
    model = Habilidad
    extra = 1  # Muestra una fila vacía lista para llenar
    autocomplete_fields = ['conocimiento'] # Permite buscar el conocimiento escribiendo

# 4. Configuración del Recurso (Empleado) + La Matriz
@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    
    list_display = ('nombre', 'perfil', 'email', 'activo') 
    list_filter = ('perfil', 'activo')
    search_fields = ('nombre', 'email')
    
    inlines = [HabilidadInline]