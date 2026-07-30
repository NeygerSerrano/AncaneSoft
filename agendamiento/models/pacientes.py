from django.db import models

class Entidad(models.Model):
    nombre_entidad = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre_entidad

class Paciente(models.Model):
    tipo_documento = models.CharField(max_length=10)
    nro_documento = models.CharField(max_length=30, unique=True)
    nombre_completo = models.CharField(max_length=200)
    entidad = models.ForeignKey(Entidad, on_delete=models.RESTRICT)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo_electronico = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre_completo
