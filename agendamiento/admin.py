from django.contrib import admin
from .models import Rol, Entidad, Usuario, Paciente, Cita, BloqueoAgenda, LogAuditoria

# Registramos los modelos para que aparezcan en el panel de Django
admin.site.register(Rol)
admin.site.register(Entidad)
admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(BloqueoAgenda)
admin.site.register(LogAuditoria)