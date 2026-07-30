from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre_rol

class Usuario(AbstractUser):
    # Campos que se suman a los que ya trae AbstractUser (username, password, is_active, etc.)
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, null=True, blank=True)
    tipo_documento = models.CharField(max_length=10)
    nro_documento = models.CharField(max_length=30, unique=True)
    
    # Resolviendo conflictos con los groups y user_permissions de Django
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuario_set',
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario',
    )

    def __str__(self):
        rol_nombre = self.rol.nombre_rol if self.rol else 'Sin Rol'
        return f"{self.first_name} {self.last_name} - {rol_nombre}"
