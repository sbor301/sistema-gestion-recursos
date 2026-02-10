from django.db import models
from datetime import date
from rrhh.models import Recurso, Conocimiento

class Cliente(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Cliente")
    contacto_principal = models.CharField(max_length=100, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)

    # 1. Definimos las opciones fijas 
    OPCIONES_UNIDAD = [
        ('AUTOMATIZACION', 'Automatización'),
        ('TELECOMUNICACIONES', 'Telecomunicaciones'),
        ('ENERGIA', 'Energía'),
    ]
    
    centro_costo = models.CharField(
        max_length=100, 
        verbose_name="Centro de Costo",
        help_text="Ej: AU43388, AGRO10002, AU43399",
        default="General"  
    )
    
    unidad_negocio = models.CharField(
        max_length=20,
        choices=OPCIONES_UNIDAD,
        default='AUTOMATIZACION',
        verbose_name="Unidad de Negocio"
    )

    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proyectos',
        verbose_name="Cliente Asignado"
    )

    fecha_inicio = models.DateField()
    fecha_fin_estimada = models.DateField()
    descripcion = models.TextField(blank=True)

    def __str__(self):
        cliente_str = f" - {self.cliente.nombre}" if self.cliente else ""
        return f"{self.nombre}{cliente_str} ({self.centro_costo})"

class Tarea(models.Model):
    nombre = models.CharField(max_length=200)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    
    # Aquí es donde asignamos: "Esta tarea es para Jairo"
    asignado_a = models.ForeignKey(Recurso, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsable")
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Lógica de Predecesoras 
    predecesora = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sucesoras')
    
    progreso = models.IntegerField(default=0, help_text="% Completado")

    requisitos = models.ManyToManyField(Conocimiento, blank=True, verbose_name="Conocimientos Requeridos")

    @property
    def estado_actual(self):
        """Calcula el estado en tiempo real basado en fechas y progreso"""
        hoy = date.today()
        
        if self.progreso == 100:
            return 'COMPLETADO'
        elif self.fecha_fin < hoy:
            return 'ATRASADO'
        elif self.progreso > 0:
            return 'EN_CURSO'
        elif self.fecha_inicio <= hoy:
            return 'INICIANDO' 
        else:
            return 'PENDIENTE' 

    def __str__(self):
        return f"{self.nombre} - {self.asignado_a}"