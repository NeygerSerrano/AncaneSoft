from .auth_views import login_view, logout_view, solicitar_recuperacion, ingresar_codigo, restablecer_contrasena
from .dashboard_views import dashboard_view
from .citas_views import (
    agenda_view, api_citas, citas_list_view, cancelar_cita_view,
    reagendar_cita_view, bloquear_agenda_view, desbloquear_agenda_view,
    api_buscar_paciente, enviar_recordatorio_view, atender_cita_view
)
from .pacientes_views import pacientes_view, historial_paciente_view, editar_paciente_view
from .config_views import configuracion_view, soporte_view, reportes_view, exportar_reporte_excel
