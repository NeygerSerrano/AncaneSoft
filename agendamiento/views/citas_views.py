from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import is_aware, make_aware, get_current_timezone
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from ..models import Cita, Paciente, BloqueoAgenda, LogAuditoria, Entidad
from ..services import is_time_slot_available
from ..decorators import rol_requerido

def agenda_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        if request.user.rol and request.user.rol.nombre_rol != 'Secretaria':
            messages.error(request, 'Solo la Secretaria tiene permisos para agendar citas.')
            return redirect('agenda')
        
        nro_doc = request.POST.get('nro_documento')
        tipo_doc = request.POST.get('tipo_documento', 'CC')
        nombre = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo_electronico')
        entidad_id = request.POST.get('entidad')
        
        if entidad_id:
            entidad = Entidad.objects.get(id=entidad_id)
        else:
            entidad, _ = Entidad.objects.get_or_create(nombre_entidad='Particular')
        
        paciente, created = Paciente.objects.get_or_create(
            nro_documento=nro_doc,
            defaults={
                'tipo_documento': tipo_doc,
                'nombre_completo': nombre,
                'telefono': telefono,
                'correo_electronico': correo,
                'entidad': entidad
            }
        )
        
        # Actualizar datos si el paciente ya existe y vienen en el form
        if not created:
            updated = False
            if correo and paciente.correo_electronico != correo:
                paciente.correo_electronico = correo
                updated = True
            if telefono and paciente.telefono != telefono:
                paciente.telefono = telefono
                updated = True
            if entidad_id and paciente.entidad_id != int(entidad_id):
                paciente.entidad_id = entidad_id
                updated = True
            if updated:
                paciente.save()
        
        tipo_cita = request.POST.get('tipo_cita')
        motivo = request.POST.get('motivo_cita')
        fecha_inicio = parse_datetime(request.POST.get('fecha_hora_inicio'))
        fecha_fin = parse_datetime(request.POST.get('fecha_hora_fin'))
        
        if not is_aware(fecha_inicio):
            fecha_inicio = make_aware(fecha_inicio, get_current_timezone())
        if not is_aware(fecha_fin):
            fecha_fin = make_aware(fecha_fin, get_current_timezone())
            
        disponible, msg = is_time_slot_available(fecha_inicio, fecha_fin)
        if not disponible:
            messages.error(request, f"No se pudo agendar: {msg}")
            return redirect('agenda')
        
        cita = Cita.objects.create(
            paciente=paciente,
            usuario_agendo=request.user,
            tipo_cita=tipo_cita,
            motivo_cita=motivo,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='Programada'
        )
        
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR_CITA',
            tabla_afectada='Cita',
            id_registro_afectado=cita.id,
            detalles='Cita agendada desde el calendario.'
        )
        
        # ENVIAR EMAIL DE CONFIRMACIÓN
        if paciente.correo_electronico:
            from django.core.mail import send_mail
            from django.conf import settings
            asunto = f"Confirmación de Cita - MediQQTA"
            mensaje = f"Hola {paciente.nombre_completo},\n\nTu cita de {tipo_cita} ha sido agendada con éxito para el día {fecha_inicio.strftime('%Y-%m-%d a las %H:%M')}.\n\n¡Te esperamos!"
            try:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@mediqqta.com', [paciente.correo_electronico])
            except Exception as e:
                print("Error enviando correo:", e)
        
        messages.success(request, 'Cita agendada correctamente.')
        return redirect('agenda')
        
    entidades = Entidad.objects.all()
    return render(request, 'agendamiento/agenda.html', {'entidades': entidades})

@login_required
def api_citas(request):
    from ..models import ConfiguracionSistema
    
    start = request.GET.get('start')
    end = request.GET.get('end')
    eventos = []
    
    config = ConfiguracionSistema.load()
    color_primario = config.color_primario if config.color_primario else '#1d8797'
    color_secundario = config.color_secundario if config.color_secundario else '#0f3856'
    
    citas = Cita.objects.select_related('paciente')
    if start and end:
        citas = citas.filter(fecha_hora_inicio__gte=start, fecha_hora_fin__lte=end)
        
    for cita in citas:
        if cita.estado == 'Cancelada':
            color = '#ef4444' # Rojo para canceladas
        else:
            color = color_primario if cita.tipo_cita == 'Valoración' else color_secundario
            
        if request.user.rol and request.user.rol.nombre_rol == 'Recepcionista':
            extended_props = {'estado': cita.estado}
        else:
            extended_props = {
                'tipo': 'cita',
                'estado': cita.estado,
                'telefono': cita.paciente.telefono,
                'motivo': cita.motivo_cita,
                'tipo_cita': cita.tipo_cita
            }
            
        eventos.append({
            'id': f'cita_{cita.id}',
            'title': cita.paciente.nombre_completo,
            'start': cita.fecha_hora_inicio.isoformat(),
            'end': cita.fecha_hora_fin.isoformat(),
            'color': color,
            'extendedProps': extended_props
        })
        
    bloqueos = BloqueoAgenda.objects.all()
    if start and end:
        bloqueos = bloqueos.filter(fecha_hora_inicio__gte=start, fecha_hora_fin__lte=end)
        
    for bloqueo in bloqueos:
        eventos.append({
            'id': f'bloqueo_{bloqueo.id}',
            'title': f'BLOQUEO: {bloqueo.motivo_bloqueo or "No disponible"}',
            'start': bloqueo.fecha_hora_inicio.isoformat(),
            'end': bloqueo.fecha_hora_fin.isoformat(),
            'color': '#717973',
            'display': 'background'
        })
        
    return JsonResponse(eventos, safe=False)

@login_required
@rol_requerido(['Secretaria', 'Doctora'])
def citas_list_view(request):
    citas = Cita.objects.all().select_related('paciente', 'usuario_agendo').order_by('-fecha_hora_inicio')
    return render(request, 'agendamiento/citas_list.html', {'citas': citas})

@login_required
@rol_requerido(['Secretaria'])
def cancelar_cita_view(request, cita_id):
    if request.method == 'POST':
        motivo = request.POST.get('motivo_cancelacion')
        try:
            cita = Cita.objects.get(id=cita_id)
            cita.estado = 'Cancelada'
            cita.motivo_cancelacion = motivo
            cita.save()
            
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='CANCELAR_CITA',
                tabla_afectada='Cita',
                id_registro_afectado=cita.id,
                detalles=f'Cita cancelada. Motivo: {motivo}'
            )
            
            messages.success(request, 'Cita cancelada con éxito.')
        except Cita.DoesNotExist:
            messages.error(request, 'Cita no encontrada.')
            
    return redirect('agenda')

@login_required
@rol_requerido(['Secretaria'])
def enviar_recordatorio_view(request, cita_id):
    if request.method == 'POST':
        try:
            cita = Cita.objects.select_related('paciente').get(id=cita_id)
            if cita.paciente.correo_electronico:
                from django.core.mail import send_mail
                from django.conf import settings
                asunto = f"Recordatorio de Cita - MediQQTA"
                mensaje = f"Hola {cita.paciente.nombre_completo},\n\nTe recordamos tu cita de {cita.tipo_cita} agendada para el día {cita.fecha_hora_inicio.strftime('%Y-%m-%d a las %H:%M')}.\n\n¡Te esperamos!"
                try:
                    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@mediqqta.com', [cita.paciente.correo_electronico])
                    messages.success(request, 'Recordatorio enviado con éxito al paciente.')
                except Exception as e:
                    messages.error(request, f'Error al enviar recordatorio: {e}')
            else:
                messages.error(request, 'El paciente no tiene un correo electrónico registrado.')
        except Cita.DoesNotExist:
            messages.error(request, 'Cita no encontrada.')
            
    return redirect('agenda')

@login_required
@rol_requerido(['Secretaria'])
def reagendar_cita_view(request, cita_id):
    if request.method == 'POST':
        try:
            cita = Cita.objects.get(id=cita_id)
            fecha_inicio = parse_datetime(request.POST.get('fecha_hora_inicio'))
            fecha_fin = parse_datetime(request.POST.get('fecha_hora_fin'))
            
            if not is_aware(fecha_inicio):
                fecha_inicio = make_aware(fecha_inicio, get_current_timezone())
            if not is_aware(fecha_fin):
                fecha_fin = make_aware(fecha_fin, get_current_timezone())
                
            disponible, msg = is_time_slot_available(fecha_inicio, fecha_fin, exclude_cita_id=cita.id)
            if not disponible:
                messages.error(request, f"No se pudo reagendar: {msg}")
                return redirect('agenda')
                
            old_start = cita.fecha_hora_inicio
            cita.fecha_hora_inicio = fecha_inicio
            cita.fecha_hora_fin = fecha_fin
            cita.estado = 'Reprogramada'
            cita.save()
            
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='REAGENDAR_CITA',
                tabla_afectada='Cita',
                id_registro_afectado=cita.id,
                detalles=f'Fecha original: {old_start.strftime("%Y-%m-%d %H:%M")}'
            )
            messages.success(request, 'Cita reagendada correctamente.')
        except Cita.DoesNotExist:
            messages.error(request, 'La cita no existe.')
            
    return redirect('agenda')

@login_required
@rol_requerido(['Doctora'])
def bloquear_agenda_view(request):
    if request.method == 'POST':
        fecha_inicio = parse_datetime(request.POST.get('fecha_hora_inicio'))
        fecha_fin = parse_datetime(request.POST.get('fecha_hora_fin'))
        motivo = request.POST.get('motivo_bloqueo', 'Bloqueado por Doctora')
        
        if not is_aware(fecha_inicio):
            fecha_inicio = make_aware(fecha_inicio, get_current_timezone())
        if not is_aware(fecha_fin):
            fecha_fin = make_aware(fecha_fin, get_current_timezone())
            
        disponible, msg = is_time_slot_available(fecha_inicio, fecha_fin)
        if not disponible:
            messages.error(request, f"No se puede bloquear: {msg}")
            return redirect('agenda')
            
        BloqueoAgenda.objects.create(
            usuario_doctora=request.user,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            motivo_bloqueo=motivo
        )
        messages.success(request, 'Horario bloqueado exitosamente.')
        
    return redirect('agenda')

@login_required
@rol_requerido(['Doctora'])
def desbloquear_agenda_view(request, bloqueo_id):
    try:
        bloqueo = BloqueoAgenda.objects.get(id=bloqueo_id)
        bloqueo.delete()
        messages.success(request, 'Horario desbloqueado exitosamente.')
    except BloqueoAgenda.DoesNotExist:
        messages.error(request, 'El bloqueo no existe.')
    return redirect('agenda')

@login_required
def api_buscar_paciente(request):
    nro_documento = request.GET.get('nro_documento')
    if not nro_documento:
        return JsonResponse({'error': 'Número de documento requerido'}, status=400)
    
    try:
        paciente = Paciente.objects.get(nro_documento=nro_documento)
        return JsonResponse({
            'encontrado': True,
            'nombre_completo': paciente.nombre_completo,
            'telefono': paciente.telefono,
            'tipo_documento': paciente.tipo_documento,
            'correo_electronico': paciente.correo_electronico,
            'entidad_id': paciente.entidad_id
        })
    except Paciente.DoesNotExist:
        return JsonResponse({'encontrado': False})
