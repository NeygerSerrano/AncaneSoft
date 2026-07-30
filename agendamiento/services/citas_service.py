from django.db.models import Q
from django.utils import timezone
from ..models import Cita, BloqueoAgenda

def is_time_slot_available(inicio, fin, exclude_cita_id=None):
    """
    Verifica si un rango de tiempo está disponible en la agenda.
    Comprueba cruces con otras citas (Programadas/Atendidas) y con Bloqueos de Agenda.
    """
    # 1. Validar reglas de negocio generales
    # - Horario de atención: 7:00 a.m. a 8:00 p.m. (20:00)
    # - Días de atención: Lunes(0) a Sábado(5). Domingo(6) está cerrado.
    if inicio.weekday() == 6 or fin.weekday() == 6:
        return False, "El consultorio no atiende los domingos."
    
    if inicio.hour < 7 or fin.hour > 20 or (fin.hour == 20 and fin.minute > 0):
        return False, "El horario seleccionado está fuera del horario de atención (7:00 AM - 8:00 PM)."

    if inicio >= fin:
        return False, "La hora de inicio debe ser menor a la hora de fin."

    # 2. Validar cruces con citas existentes
    # Citas que se solapan y no están canceladas
    citas_solapadas = Cita.objects.filter(
        Q(estado='Programada') | Q(estado='Atendida') | Q(estado='Reprogramada'),
        fecha_hora_inicio__lt=fin,
        fecha_hora_fin__gt=inicio
    )
    
    if exclude_cita_id:
        citas_solapadas = citas_solapadas.exclude(id=exclude_cita_id)
        
    if citas_solapadas.exists():
        return False, "El horario seleccionado choca con otra cita programada."

    # 3. Validar cruces con bloqueos de agenda
    bloqueos_solapados = BloqueoAgenda.objects.filter(
        fecha_hora_inicio__lt=fin,
        fecha_hora_fin__gt=inicio
    )
    if bloqueos_solapados.exists():
        return False, "El horario seleccionado está bloqueado por la Doctora."

    return True, "Horario disponible"
