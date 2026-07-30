from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from ..models import Cita
from ..decorators import rol_requerido
import csv

@login_required
@rol_requerido(['Doctora'])
def reportes_view(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    estado = request.GET.get('estado')
    
    hoy = timezone.now()
    if not mes:
        mes = str(hoy.month)
    if not anio:
        anio = str(hoy.year)
        
    citas = Cita.objects.filter(fecha_hora_inicio__year=anio, fecha_hora_inicio__month=mes)
    if estado:
        citas = citas.filter(estado=estado)
        
    citas = citas.select_related('paciente').order_by('fecha_hora_inicio')
    
    context = {
        'citas': citas,
        'mes_seleccionado': int(mes),
        'anio_seleccionado': int(anio),
        'estado_seleccionado': estado,
        'total_citas': citas.count(),
        'total_atendidas': citas.filter(estado='Atendida').count(),
        'total_canceladas': citas.filter(estado='Cancelada').count(),
    }
    return render(request, 'agendamiento/reportes.html', context)

@login_required
@rol_requerido(['Doctora'])
def exportar_reporte_csv(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    estado = request.GET.get('estado')
    
    hoy = timezone.now()
    if not mes:
        mes = str(hoy.month)
    if not anio:
        anio = str(hoy.year)
        
    citas = Cita.objects.filter(fecha_hora_inicio__year=anio, fecha_hora_inicio__month=mes)
    if estado:
        citas = citas.filter(estado=estado)
        
    citas = citas.select_related('paciente').order_by('fecha_hora_inicio')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_citas_{anio}_{mes}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Fecha y Hora', 'Paciente', 'Tipo Cita', 'Estado', 'Motivo'])
    
    for cita in citas:
        writer.writerow([
            cita.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M'),
            cita.paciente.nombre_completo,
            cita.tipo_cita,
            cita.estado,
            cita.motivo_cita or ''
        ])
        
    return response
