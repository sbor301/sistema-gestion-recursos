# proyectos/services.py
import openpyxl
from datetime import datetime
from rrhh.models import Recurso, Habilidad, Conocimiento, Perfil
from .models import Proyecto

def procesar_excel_recursos(archivo_excel):
    wb = openpyxl.load_workbook(archivo_excel)
    ws = wb.active
    creados = 0
    actualizados = 0
    errores = []

    for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            nombre = row[0]
            nombre_perfil = row[1]
            email_excel = row[2]
            habilidades_str = row[3]

            if not nombre: continue

            # Lógica Perfil
            perfil_obj = None
            if nombre_perfil:
                perfil_obj, _ = Perfil.objects.get_or_create(nombre=nombre_perfil)

            # Lógica Recurso
            recurso, created = Recurso.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'perfil': perfil_obj,
                    'email': email_excel if email_excel else "",
                    'activo': True
                }
            )
            if created: creados += 1
            else: actualizados += 1

            # Lógica Habilidades
            if habilidades_str:
                lista_skills = str(habilidades_str).split(',')
                for skill_raw in lista_skills:
                    skill_data = skill_raw.strip()
                    if not skill_data: continue
                    
                    if ':' in skill_data:
                        partes = skill_data.split(':')
                        nombre_skill = partes[0].strip()
                        try: nivel_skill = int(partes[1].strip())
                        except: nivel_skill = 1
                    else:
                        nombre_skill = skill_data
                        nivel_skill = 1

                    conocimiento_obj, _ = Conocimiento.objects.get_or_create(nombre=nombre_skill)
                    Habilidad.objects.update_or_create(recurso=recurso, conocimiento=conocimiento_obj, defaults={'nivel': nivel_skill})

        except Exception as e:
            errores.append(f"Fila {index} ({nombre}): {str(e)}")

    return {'creados': creados, 'actualizados': actualizados, 'errores': errores}

def procesar_excel_proyectos(archivo_excel):
    wb = openpyxl.load_workbook(archivo_excel)
    ws = wb.active
    creados = 0
    actualizados = 0
    errores = []

    def limpiar_fecha(valor, default):
        if not valor: return default
        if isinstance(valor, datetime) or hasattr(valor, 'date'): return valor
        try: return datetime.strptime(str(valor).strip(), '%Y-%m-%d').date()
        except: return default

    hoy = datetime.now().date()

    for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            nombre = row[0]
            centro_costo = row[1]
            f_inicio_raw = row[2]
            f_fin_raw = row[3]
            unidad_raw = row[4]

            if not nombre: continue

            f_inicio = limpiar_fecha(f_inicio_raw, hoy)
            f_fin = limpiar_fecha(f_fin_raw, hoy)

            unidad_final = 'AUTOMATIZACION'
            if unidad_raw:
                texto_limpio = str(unidad_raw).upper().strip()
                mapa_unidades = {
                    'ENERGIA': 'ENERGIA', 'ENERGÍA': 'ENERGIA',
                    'TELECOMUNICACIONES': 'TELECOMUNICACIONES', 'TELECOM': 'TELECOMUNICACIONES',
                    'AUTOMATIZACION': 'AUTOMATIZACION', 'AUTOMATIZACIÓN': 'AUTOMATIZACION'
                }
                unidad_final = mapa_unidades.get(texto_limpio, 'AUTOMATIZACION')

            obj, created = Proyecto.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'centro_costo': centro_costo if centro_costo else "General",
                    'fecha_inicio': f_inicio,
                    'fecha_fin_estimada': f_fin,
                    'unidad_negocio': unidad_final,
                }
            )
            if created: creados += 1
            else: actualizados += 1

        except Exception as e:
            errores.append(f"Fila {index} ({nombre}): {str(e)}")

    return {'creados': creados, 'actualizados': actualizados, 'errores': errores}