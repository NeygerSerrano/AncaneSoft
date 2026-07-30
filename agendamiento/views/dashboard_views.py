from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from ..models import Cita

@login_required
def dashboard_view(request):
    # Si es recepcionista, redirigir a la agenda
    if request.user.rol and request.user.rol.nombre_rol == 'Recepcionista':
        return redirect('agenda')

    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # Citas del mes actual
    citas_mes = Cita.objects.filter(fecha_hora_inicio__year=anio_actual, fecha_hora_inicio__month=mes_actual)
    
    # 1. Citas del mes (agendadas/programadas)
    citas_programadas = citas_mes.filter(estado='Programada').count()
    
    # 2. Citas canceladas
    citas_canceladas = citas_mes.filter(estado='Cancelada').count()
    
    # 3. Citas reprogramadas
    citas_reprogramadas = citas_mes.filter(estado='Reprogramada').count()
    
    # 4. Tratamiento más frecuente del mes
    top_tratamiento = citas_mes.values('tipo_cita').annotate(total=Count('tipo_cita')).order_by('-total').first()
    top_tratamiento_nombre = top_tratamiento['tipo_cita'] if top_tratamiento else 'N/A'
    
    # 5. Próximas Citas de la semana
    inicio_dia = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_semana = inicio_dia + timezone.timedelta(days=7)
    proximas_citas = Cita.objects.filter(
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_inicio__lte=fin_semana,
        estado='Programada'
    ).select_related('paciente').order_by('fecha_hora_inicio')

    context = {
        'citas_programadas': citas_programadas,
        'citas_canceladas': citas_canceladas,
        'citas_reprogramadas': citas_reprogramadas,
        'top_tratamiento': top_tratamiento_nombre,
        'proximas_citas': proximas_citas,
    }
    return render(request, 'agendamiento/dashboard.html', context)
