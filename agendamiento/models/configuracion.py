from django.db import models
from .usuarios import Usuario

class LogAuditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=50)
    tabla_afectada = models.CharField(max_length=50)
    id_registro_afectado = models.IntegerField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} por {self.usuario}"

class ConfiguracionSistema(models.Model):
    """
    Modelo Singleton para almacenar configuraciones globales del sistema como los colores corporativos.
    """
    color_primario = models.CharField(max_length=20, default="#1d8797", help_text="Color principal (ej. Diente, botones)")
    color_secundario = models.CharField(max_length=20, default="#0f3856", help_text="Color secundario (ej. Reloj, sidebar, textos)")
    nombre_clinica = models.CharField(max_length=100, default="MediQQTA", help_text="Nombre de la Clínica o Consultorio")
    
    def save(self, *args, **kwargs):
        # Asegurarnos de que solo exista un registro
        self.pk = 1
        super(ConfiguracionSistema, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Configuración: {self.nombre_clinica}"
