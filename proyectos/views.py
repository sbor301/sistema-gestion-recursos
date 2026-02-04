from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder
from .models import Tarea, Proyecto
from rrhh.models import Recurso, Perfil, Habilidad
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import date
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import json

def vista_gantt(request):
    # 1. Capturar filtros de la URL
    proyecto_id = request.GET.get('proyecto')
    recurso_id = request.GET.get('recurso')
    
    # 2. Consulta Base
    tareas = Tarea.objects.all().select_related('proyecto', 'asignado_a')
    
    # 3. Aplicar Filtros
    if proyecto_id:
        tareas = tareas.filter(proyecto_id=proyecto_id)
    if recurso_id:
        tareas = tareas.filter(asignado_a_id=recurso_id)
        
    # 4. Preparar datos para JavaScript (Frappe Gantt format)
    gantt_data = []
    for t in tareas:
        gantt_data.append({
            'id': str(t.id),
            'name': f"{t.nombre}",
            'start': t.fecha_inicio.strftime("%Y-%m-%d"),
            'end': t.fecha_fin.strftime("%Y-%m-%d"),
            'progress': t.progreso,
            # Usamos colores diferentes según el proyecto (truco visual)
            'custom_class': f'bar-project-{t.proyecto.id % 5}', 
            # Información extra para el tooltip
            'proyecto': t.proyecto.nombre,
            'responsable': t.asignado_a.nombre if t.asignado_a else "Sin asignar"
        })
        
    # 5. Listas para los selectores del filtro
    proyectos = Proyecto.objects.all()
    recursos = Recurso.objects.all()

    contexto = {
        'gantt_data': json.dumps(gantt_data, cls=DjangoJSONEncoder),
        'proyectos': proyectos,
        'recursos': recursos,
        'filtros': {'proyecto': proyecto_id, 'recurso': recurso_id} # Para mantener seleccionado el filtro
    }
    
    return render(request, 'proyectos/gantt.html', contexto)

def buscar_disponibilidad(request):
    # ---INICIALIZACIÓN ---
    candidatos_finales = []
    mensaje = ""
    tarea_obj = None
    # Capturamos fechas y perfil
    fecha_inicio_req = request.GET.get('fecha_inicio')
    fecha_fin_req = request.GET.get('fecha_fin')
    perfil_id = request.GET.get('perfil_id')
    tarea_id = request.GET.get('tarea_id')
    
    # --- 2. RECUPERAR TAREA Y REQUISITOS ---
    requisitos = []
    if tarea_id:
        try:
            tarea_obj = Tarea.objects.get(id=tarea_id)
            if not fecha_inicio_req: fecha_inicio_req = tarea_obj.fecha_inicio.strftime('%Y-%m-%d')
            if not fecha_fin_req: fecha_fin_req = tarea_obj.fecha_fin.strftime('%Y-%m-%d')
            requisitos = tarea_obj.requisitos.all()
        except Tarea.DoesNotExist:
            tarea_obj = None

    # --- 3. LÓGICA DE BÚSQUEDA ---
    if fecha_inicio_req and fecha_fin_req:
        if fecha_inicio_req > fecha_fin_req:
            mensaje = "Error: La fecha de inicio no puede ser mayor al fin."
        else:
            # A. TRAEMOS A TODOS (Activos)
            recursos = Recurso.objects.filter(activo=True)

            if perfil_id:
                recursos = recursos.filter(perfil_id=perfil_id)

            # B. IDENTIFICAMOS A LOS OCUPADOS (Solo para marcar, no para borrar)
            ocupados_ids = Tarea.objects.filter(
                fecha_inicio__lte=fecha_fin_req,
                fecha_fin__gte=fecha_inicio_req,
                progreso__lt=100
            ).values_list('asignado_a_id', flat=True)

            # C. PROCESAMOS A CADA RECURSO
            for recurso in recursos:
                # 1. Calculamos Disponibilidad Básica
                esta_ocupado = recurso.id in ocupados_ids
                
                # --- CALCULAR CUÁNDO SE LIBERA ---
                fecha_liberacion = None
                nombre_tarea_actual = ""
                
                if esta_ocupado:
                    # Buscamos la tarea que termina más tarde dentro del rango conflicto
                    ultima_tarea = Tarea.objects.filter(
                        asignado_a=recurso,
                        progreso__lt=100,
                        fecha_fin__gte=fecha_inicio_req  # Tareas que terminan después del inicio buscado
                    ).order_by('-fecha_fin').first()
                    
                    if ultima_tarea:
                        fecha_liberacion = ultima_tarea.fecha_fin
                        nombre_tarea_actual = ultima_tarea.nombre
                
                # 2. Calculamos Match Técnico 
                match_score = 0
                detalles = []
                
                if requisitos:
                    puntos_totales = 0
                    for req in requisitos:
                        habilidad = Habilidad.objects.filter(recurso=recurso, conocimiento=req).first()
                        if habilidad:
                            puntos = (habilidad.nivel / 5) * 100
                            puntos_totales += puntos
                            detalles.append({'skill': req.nombre, 'nivel': habilidad.get_nivel_display(), 'cumple': True})
                        else:
                            detalles.append({'skill': req.nombre, 'nivel': '---', 'cumple': False})
                    match_score = round(puntos_totales / len(requisitos))
                else:
                    match_score = 100 

                candidatos_finales.append({
                    'perfil': recurso,
                    'match': match_score,
                    'ocupado': esta_ocupado,
                    'fecha_liberacion': fecha_liberacion, 
                    'tarea_actual': nombre_tarea_actual,  
                    'detalles': detalles
                })

            # D. ORDENAMIENTO INTELIGENTE
            # Primero por Match (Mayor a menor), luego por Disponibilidad (Libres primero)
            candidatos_finales.sort(key=lambda x: (not x['ocupado'], x['match']), reverse=True)

            if not candidatos_finales:
                 mensaje = "No se encontraron recursos activos con ese perfil."

    # --- 4. CONTEXTO ---
    perfiles = Perfil.objects.all()
    contexto = {
        'perfiles': perfiles,
        'candidatos': candidatos_finales,
        'mensaje': mensaje,
        'tarea_seleccionada': tarea_obj,
        'filtros': {'fecha_inicio': fecha_inicio_req, 'fecha_fin': fecha_fin_req, 'perfil': int(perfil_id) if perfil_id else ''}
    }
    return render(request, 'proyectos/buscar.html', contexto)

# 2. PONEMOS @require_POST (Para que solo acepte envíos de datos, no visitas por navegador)
@require_POST
def actualizar_tarea_api(request):
    # El resto del código queda IGUAL
    try:
        data = json.loads(request.body)
        tarea_id = data.get('id')
        nueva_fecha_inicio = data.get('start')
        nueva_fecha_fin = data.get('end')
        
        tarea = Tarea.objects.get(id=tarea_id)
        tarea.fecha_inicio = nueva_fecha_inicio[:10]
        tarea.fecha_fin = nueva_fecha_fin[:10]
        tarea.save()
        
        return JsonResponse({'status': 'ok'})
    except Tarea.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Tarea no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)

def asignar_recurso(request, tarea_id, recurso_id):
    tarea = Tarea.objects.get(id=tarea_id)
    recurso = Recurso.objects.get(id=recurso_id)
    
    tarea.asignado_a = recurso
    tarea.save()

    messages.success(request, f"¡Éxito! La tarea '{tarea.nombre}' ha sido asignada a {recurso.nombre}.")
    
    # Nos devuelve al Gantt para ver el cambio
    return redirect('gantt')

def index(request):
    # Contadores para el Dashboard
    total_proyectos = Proyecto.objects.count()
    total_tareas = Tarea.objects.count()
    total_recursos = Recurso.objects.count()
    
    # Calculamos progreso promedio (opcional)
    # Esto es solo un ejemplo, puedes simplificarlo
    tareas_completadas = Tarea.objects.filter(progreso=100).count()

    # --- Agrupar por Centro de Costo ---
    # Esto crea una lista como: [{'centro_costo': 'TI', 'total': 5}, {'centro_costo': 'Obras', 'total': 2}]
    centros_unicos = Proyecto.objects.values_list('centro_costo', flat=True).distinct()

    datos_agrupados = []
    for cc in centros_unicos:
        # Buscamos los proyectos de este centro
        proyectos = Proyecto.objects.filter(centro_costo=cc)
        
        datos_agrupados.append({
            'nombre_cc': cc,
            'cantidad': proyectos.count(),
            'lista_proyectos': proyectos 
        })
    
    contexto = {
        'total_proyectos': total_proyectos,
        'total_tareas': total_tareas,
        'total_recursos': total_recursos,
        'tareas_completadas': tareas_completadas,
        'proyectos_por_cc': datos_agrupados,
    }
    
    return render(request, 'proyectos/index.html', contexto)

def ver_recursos(request):
    hoy = timezone.now().date()
    recursos = Recurso.objects.all()
    info_recursos = []
    
    for r in recursos:
        # 1. Tareas ACTIVAS (Las que hacen que esté "Ocupado" HOY)
        # Criterio: Ya empezó, no ha terminado su fecha fin, y no está al 100%
        tareas_activas = Tarea.objects.filter(
            asignado_a=r,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            progreso__lt=100
        )

        # 2. Tareas FUTURAS (Solo informativas, no afectan el estado de hoy)
        # Criterio: Empiezan DESPUÉS de hoy
        tareas_futuras = Tarea.objects.filter(
            asignado_a=r,
            fecha_inicio__gt=hoy,
            progreso__lt=100
        ).order_by('fecha_inicio')[:3] 
        
        # Determinar el estado según las tareas ACTIVAS
        estado_actual = 'Ocupado' if tareas_activas.exists() else 'Disponible'

        info_recursos.append({
            'perfil': r,
            'estado': estado_actual,
            'tareas_activas': tareas_activas,
            'tareas_futuras': tareas_futuras 
        })
    
    contexto = {'lista_recursos': info_recursos}
    return render(request, 'proyectos/recursos.html', contexto)

def lista_proyectos(request):
    # Traemos proyectos con sus tareas pre-cargadas para optimizar velocidad
    proyectos = Proyecto.objects.prefetch_related('tareas__asignado_a').all()
    
    # Calculamos el avance promedio del proyecto (Opcional, pero útil)
    for p in proyectos:
        total_tareas = p.tareas.count()
        if total_tareas > 0:
            suma_progreso = sum(t.progreso for t in p.tareas.all())
            p.avance_total = round(suma_progreso / total_tareas)
        else:
            p.avance_total = 0

    return render(request, 'proyectos/lista_proyectos.html', {'proyectos': proyectos})

def reporte_recurso(request):
    recursos = Recurso.objects.all()
    
    # Filtros recibidos
    recurso_id = request.GET.get('recurso')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    exportar_excel = request.GET.get('exportar') == 'excel' # Detectar si pidieron Excel
    
    # 1. Determinar qué recursos vamos a procesar
    if recurso_id:
        recursos_filtrados = Recurso.objects.filter(id=recurso_id)
    else:
        # Si no selecciona nada, son TODOS (pero solo si presionó Generar o Excel)
        if request.GET: 
            recursos_filtrados = Recurso.objects.all()
        else:
            recursos_filtrados = [] # Al entrar por primera vez, no mostramos nada

    datos_reporte = []

    # 2. Procesamos la información para cada recurso encontrado
    for recurso in recursos_filtrados:
        tareas = Tarea.objects.filter(asignado_a=recurso).order_by('-fecha_fin')
        
        if fecha_inicio:
            tareas = tareas.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            tareas = tareas.filter(fecha_fin__lte=fecha_fin)
            
        # Estadísticas
        total_tareas = tareas.count()
        completadas = tareas.filter(progreso=100).count()
        pendientes = total_tareas - completadas
        rendimiento = round((completadas / total_tareas * 100), 1) if total_tareas > 0 else 0
        
        datos_reporte.append({
            'recurso': recurso,
            'tareas': tareas,
            'stats': {
                'total': total_tareas,
                'completadas': completadas,
                'pendientes': pendientes,
                'rendimiento': rendimiento
            }
        })

    # ... (código anterior en views.py) ...

    # --- LÓGICA DE EXCEL ---
    if exportar_excel and datos_reporte:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte de Recursos"

        # Estilos para el Excel
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="0d6efd", end_color="0d6efd", fill_type="solid")
        
        # Encabezados
        headers = ['Ingeniero/Recurso', 'Cargo/Perfil', 'Proyecto', 'Tarea', 'Inicio', 'Fin', 'Estado', 'Progreso (%)']
        ws.append(headers)

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill

        # Llenar datos
        hoy = date.today()
        for data in datos_reporte:
            r_nombre = data['recurso'].nombre
            
            # --- CORRECCIÓN AQUÍ: DETECCIÓN SEGURA DEL CARGO ---
            # Intentamos obtener 'cargo', si no existe, intentamos 'perfil', si no, ponemos 'N/A'
            try:
                r_cargo = data['recurso'].cargo
            except AttributeError:
                try:
                    # Si tu modelo usa 'perfil' en vez de cargo
                    r_cargo = str(data['recurso'].perfil) 
                except AttributeError:
                    r_cargo = "No especificado"
            # ---------------------------------------------------

            if not data['tareas']:
                ws.append([r_nombre, r_cargo, "Sin tareas", "-", "-", "-", "-", "-"])
                continue

            for t in data['tareas']:
                estado = "En Curso"
                if t.progreso == 100: estado = "Finalizado"
                elif t.fecha_fin < hoy: estado = "Atrasado"

                ws.append([
                    r_nombre,
                    r_cargo,
                    t.proyecto.nombre,
                    t.nombre,
                    t.fecha_inicio,
                    t.fecha_fin,
                    estado,
                    t.progreso
                ])

        # Ajuste de columnas
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 30

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Reporte_Recursos_RMS.xlsx'
        wb.save(response)
        return response

    # --- LÓGICA NORMAL (HTML) ---
    contexto = {
        'recursos': recursos,
        'lista_reportes': datos_reporte, 
        'mostrar_reporte': len(datos_reporte) > 0,
        'hoy': date.today(),
        'filtros': {
            'recurso': int(recurso_id) if recurso_id else "",
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
    }

    return render(request, 'proyectos/reporte_recurso.html', contexto)