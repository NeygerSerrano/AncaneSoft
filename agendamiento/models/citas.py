from django.db import models
from .usuarios import Usuario
from .pacientes import Paciente

class Cita(models.Model):
    TIPO_CITA_CHOICES = [
        ('Valoración', 'Valoración'),
        ('Procedimiento', 'Procedimiento'),
    ]
    ESTADO_CHOICES = [
        ('Programada', 'Programada'),
        ('Cancelada', 'Cancelada'),
        ('Atendida', 'Atendida'),
        ('Reprogramada', 'Reprogramada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    usuario_agendo = models.ForeignKey(Usuario, on_delete=models.RESTRICT, related_name='citas_agendadas')
    tipo_cita = models.CharField(max_length=50, choices=TIPO_CITA_CHOICES)
    motivo_cita = models.TextField(blank=True, null=True)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='Programada')
    motivo_cancelacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cita: {self.paciente.nombre_completo} - {self.fecha_hora_inicio}"

class BloqueoAgenda(models.Model):
    usuario_doctora = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='bloqueos')
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    motivo_bloqueo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Bloqueo desde {self.fecha_hora_inicio} hasta {self.fecha_hora_fin}"
