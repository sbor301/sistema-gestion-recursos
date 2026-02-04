from django.db import models

class Perfil(models.Model):
    """Ej: Ingeniero Junior, Técnico Nivel 3"""
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Recurso(models.Model):
    """Tus empleados (Alejandro, Jairo, etc.)"""
    nombre = models.CharField(max_length=100)
    perfil = models.ForeignKey(Perfil, on_delete=models.PROTECT, verbose_name="Cargo/Perfil")
    email = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.perfil})"

class Conocimiento(models.Model):
    # Aquí guardaremos: "PLC S7-1200", "Red PROFIBUS DP", etc.
    nombre = models.CharField(max_length=200, unique=True)
    categoria = models.CharField(max_length=100, blank=True, help_text="Ej: 1. PLCs, 12. Redes")

    def __str__(self):
        return f"{self.categoria} - {self.nombre}"

class Habilidad(models.Model):
    # Aquí unimos al Recurso con el Conocimiento y le ponemos nota
    NIVELES = [
        (1, '1 - Básico'),
        (2, '2 - Principiante'),
        (3, '3 - Intermedio'),
        (4, '4 - Avanzado'),
        (5, '5 - Experto'),
    ]

    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name='habilidades')
    conocimiento = models.ForeignKey(Conocimiento, on_delete=models.CASCADE)
    nivel = models.IntegerField(choices=NIVELES, default=1)

    class Meta:
        unique_together = ('recurso', 'conocimiento') # Evita duplicados
        verbose_name = "Habilidad"
        verbose_name_plural = "Matriz de Habilidades"

    def __str__(self):
        return f"{self.recurso} sabe {self.conocimiento} (Nivel {self.nivel})"
