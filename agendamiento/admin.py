from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Rol, Entidad, Usuario, Paciente, Cita, BloqueoAgenda, LogAuditoria

class CustomUserAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'tipo_documento', 'nro_documento')}),
    )

# Registramos los modelos para que aparezcan en el panel de Django
admin.site.register(Rol)
admin.site.register(Entidad)
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(BloqueoAgenda)
admin.site.register(LogAuditoria)