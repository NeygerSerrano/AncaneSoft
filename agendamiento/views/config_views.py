from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.http import HttpResponse
from ..models import ConfiguracionSistema, Cita
from ..decorators import rol_requerido
import openpyxl

@login_required
@rol_requerido(['Secretaria', 'Doctora'])
def configuracion_view(request):
    config = ConfiguracionSistema.load()
    if request.method == 'POST':
        nombre_clinica = request.POST.get('nombre_clinica')
        color_primario = request.POST.get('color_primario')
        color_secundario = request.POST.get('color_secundario')
        
        if nombre_clinica:
            config.nombre_clinica = nombre_clinica
        if color_primario:
            config.color_primario = color_primario
        if color_secundario:
            config.color_secundario = color_secundario
            
        config.save()
        messages.success(request, 'Configuración actualizada correctamente.')
        return redirect('configuracion')
        
    return render(request, 'agendamiento/configuracion.html', {'config': config})

@login_required
def soporte_view(request):
    return render(request, 'agendamiento/soporte.html')

@login_required
@rol_requerido(['Doctora'])
def reportes_view(request):
    mes_str = request.GET.get('mes', timezone.now().strftime('%Y-%m'))
    
    try:
        year, month = map(int, mes_str.split('-'))
    except ValueError:
        year, month = timezone.now().year, timezone.now().month
        
    citas = Cita.objects.filter(fecha_hora_inicio__year=year, fecha_hora_inicio__month=month)
    
    totales = citas.values('estado').annotate(total=Count('estado'))
    total_dict = {item['estado']: item['total'] for item in totales}
    
    context = {
        'mes_str': mes_str,
        'totales': total_dict,
        'total_citas': sum(total_dict.values())
    }
    return render(request, 'agendamiento/reportes.html', context)

@login_required
@rol_requerido(['Doctora'])
def exportar_reporte_excel(request):
    mes_str = request.GET.get('mes', timezone.now().strftime('%Y-%m'))
    estado_filtro = request.GET.get('estado', '')
    
    try:
        year, month = map(int, mes_str.split('-'))
    except ValueError:
        year, month = timezone.now().year, timezone.now().month
        
    citas = Cita.objects.filter(fecha_hora_inicio__year=year, fecha_hora_inicio__month=month)
    
    if estado_filtro:
        citas = citas.filter(estado=estado_filtro)
        
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Reporte {mes_str}"
    
    headers = ['ID', 'Paciente', 'Documento', 'Teléfono', 'Tipo Cita', 'Estado', 'Inicio', 'Fin', 'Motivo / Cancelación']
    ws.append(headers)
    
    for cita in citas:
        ws.append([
            cita.id,
            cita.paciente.nombre_completo,
            cita.paciente.nro_documento,
            cita.paciente.telefono,
            cita.tipo_cita,
            cita.estado,
            timezone.localtime(cita.fecha_hora_inicio).strftime('%Y-%m-%d %H:%M'),
            timezone.localtime(cita.fecha_hora_fin).strftime('%Y-%m-%d %H:%M'),
            cita.motivo_cancelacion if cita.estado == 'Cancelada' else cita.motivo_cita
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Reporte_Citas_{mes_str}.xlsx'
    wb.save(response)
    
    return response
