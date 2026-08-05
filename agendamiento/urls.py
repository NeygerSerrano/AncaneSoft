# pyrefly: ignore [missing-import]
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('api/citas/', views.api_citas, name='api_citas'),
    path('api/pacientes/buscar/', views.api_buscar_paciente, name='api_buscar_paciente'),
    path('pacientes/', views.pacientes_view, name='pacientes'),
    path('pacientes/<int:paciente_id>/historial/', views.historial_paciente_view, name='historial_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente_view, name='editar_paciente'),
    path('citas/', views.citas_list_view, name='citas_list'),
    path('citas/<int:cita_id>/cancelar/', views.cancelar_cita_view, name='cancelar_cita'),
    path('citas/<int:cita_id>/atender/', views.atender_cita_view, name='atender_cita'),
    path('citas/<int:cita_id>/reagendar/', views.reagendar_cita_view, name='reagendar_cita'),
    path('citas/<int:cita_id>/recordatorio/', views.enviar_recordatorio_view, name='enviar_recordatorio'),
    path('bloquear/', views.bloquear_agenda_view, name='bloquear_agenda'),
    path('desbloquear/<int:bloqueo_id>/', views.desbloquear_agenda_view, name='desbloquear_agenda'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/exportar/', views.exportar_reporte_excel, name='exportar_reporte_excel'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('soporte/', views.soporte_view, name='soporte'),
]