from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import is_aware, make_aware, get_current_timezone, now
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os
import threading
from django.conf import settings
from ..models import Cita, Paciente, BloqueoAgenda, LogAuditoria, Entidad
from ..services import is_time_slot_available
from ..decorators import rol_requerido

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
        except Exception as e:
            print(f"Error enviando correo asíncrono: {e}")

def enviar_correo_html_async(asunto, titulo, paciente_nombre, mensaje_principal, tipo_cita, fecha_hora, destinatario):
    from ..models import ConfiguracionSistema
    try:
        config = ConfiguracionSistema.load()
        html_content = render_to_string('agendamiento/emails/correo_cita.html', {
            'asunto': asunto,
            'titulo': titulo,
            'nombre_paciente': paciente_nombre,
            'mensaje_principal': mensaje_principal,
            'tipo_cita': tipo_cita,
            'fecha_hora': fecha_hora,
            'color_primario': config.color_primario,
            'color_secundario': config.color_secundario,
            'nombre_clinica': config.nombre_clinica,
        })
        text_content = f"Hola {paciente_nombre},\n\n{mensaje_principal}\n\nTipo de cita: {tipo_cita}\nFecha y hora: {fecha_hora}\n\n¡Te esperamos!"
        email = EmailMultiAlternatives(
            asunto,
            text_content,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@mediqqta.com',
            [destinatario]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Check for dynamic logo first
        if config.logo and os.path.exists(config.logo.path):
            logo_path = config.logo.path
            filename = os.path.basename(logo_path)
        else:
            logo_path = os.path.join(settings.BASE_DIR, 'agendamiento', 'static', 'agendamiento', 'img', 'AncaneSoftv2.png')
            filename = 'AncaneSoftv2.png'
            
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
            logo = MIMEImage(logo_data)
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename=filename)
            email.attach(logo)
            
        EmailThread(email).start()
        return True
    except Exception as e:
        print(f"Error preparando correo HTML: {e}")
        return False

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
            
        if fecha_inicio < now():
            messages.error(request, "No se pueden agendar citas en fechas u horas pasadas.")
            return redirect('agenda')
            
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
        
        # ENVIAR EMAIL DE CONFIRMACIÓN (ASÍNCRONO)
        if paciente.correo_electronico:
            asunto = "Confirmación de Cita - AncaneSoft"
            titulo = "¡Cita Confirmada!"
            mensaje_principal = "Tu cita ha sido agendada con éxito."
            fecha_str = fecha_inicio.strftime('%Y-%m-%d a las %I:%M %p')
            enviar_correo_html_async(asunto, titulo, paciente.nombre_completo, mensaje_principal, tipo_cita, fecha_str, paciente.correo_electronico)
        
        messages.success(request, 'Cita agendada correctamente.')
        return redirect('agenda')
        
    entidades = Entidad.objects.all()
    return render(request, 'agendamiento/agenda.html', {'entidades': entidades})

@login_required
def api_citas(request):
    from ..models import ConfiguracionSistema
    from django.utils.timezone import now
    
    # Auto-completar citas pasadas que no fueron marcadas
    hoy = now().date()
    Cita.objects.filter(
        fecha_hora_inicio__date__lt=hoy, 
        estado__in=['Programada', 'Reprogramada']
    ).update(estado='Atendida')
    
    
    start = request.GET.get('start')
    end = request.GET.get('end')
    eventos = []
    
    config = ConfiguracionSistema.load()
    color_primario = config.color_primario if config.color_primario else '#1d8797'
    color_secundario = config.color_secundario if config.color_secundario else '#0f3856'
    
    citas = Cita.objects.select_related('paciente').exclude(estado='Cancelada')
    if start and end:
        citas = citas.filter(fecha_hora_inicio__gte=start, fecha_hora_fin__lte=end)
        
    for cita in citas:
        class_names = []
        if cita.estado == 'Cancelada':
            color = '#ef4444' # Rojo para canceladas
        elif cita.estado == 'Atendida':
            color = '#16a34a' # Verde para atendidas
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
            'classNames': class_names,
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
            'color': '#1f2937',
            'textColor': '#ffffff'
        })
        
    return JsonResponse(eventos, safe=False)

@login_required
@rol_requerido(['Secretaria', 'Doctora'])
def citas_list_view(request):
    from django.db.models import Q
    from django.utils.timezone import now
    
    # Auto-completar citas pasadas
    hoy = now().date()
    Cita.objects.filter(
        fecha_hora_inicio__date__lt=hoy, 
        estado__in=['Programada', 'Reprogramada']
    ).update(estado='Atendida')

    citas = Cita.objects.all().select_related('paciente', 'usuario_agendo').order_by('-fecha_hora_inicio')
    
    q = request.GET.get('q')
    mes = request.GET.get('mes')
    
    if q:
        citas = citas.filter(
            Q(paciente__nombre_completo__icontains=q) |
            Q(tipo_cita__icontains=q) |
            Q(estado__icontains=q)
        )
        
    if mes:
        citas = citas.filter(fecha_hora_inicio__month=mes)
        
    return render(request, 'agendamiento/citas_list.html', {
        'citas': citas,
        'q': q,
        'mes': mes
    })

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
            
            # ENVIAR EMAIL DE CANCELACIÓN (ASÍNCRONO)
            if cita.paciente.correo_electronico:
                from django.utils import timezone
                asunto = "Cita Cancelada - AncaneSoft"
                titulo = "Cita Cancelada"
                mensaje_principal = f"Te informamos que tu cita ha sido cancelada.<br><br><strong>Motivo:</strong> {motivo}"
                fecha_cancelacion_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d a las %I:%M %p')
                enviar_correo_html_async(asunto, titulo, cita.paciente.nombre_completo, mensaje_principal, cita.tipo_cita, fecha_cancelacion_str, cita.paciente.correo_electronico)
            
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
                asunto = "Recordatorio de Cita - AncaneSoft"
                titulo = "¡Recordatorio de Cita!"
                mensaje_principal = "Te recordamos que tienes una cita programada con nosotros."
                from django.utils import timezone
                local_dt = timezone.localtime(cita.fecha_hora_inicio)
                fecha_str = local_dt.strftime('%Y-%m-%d a las %I:%M %p')
                enviado = enviar_correo_html_async(asunto, titulo, cita.paciente.nombre_completo, mensaje_principal, cita.tipo_cita, fecha_str, cita.paciente.correo_electronico)
                
                if enviado:
                    messages.success(request, 'Recordatorio enviado con éxito (en proceso).')
                else:
                    messages.error(request, 'Error al enviar recordatorio. Hubo un problema con la conexión de correo.')
            else:
                messages.error(request, 'El paciente no tiene un correo electrónico registrado.')
        except Cita.DoesNotExist:
            messages.error(request, 'Cita no encontrada.')
            
    return redirect('agenda')

@login_required
@rol_requerido(['Secretaria'])
def atender_cita_view(request, cita_id):
    if request.method == 'POST':
        try:
            cita = Cita.objects.get(id=cita_id)
            if cita.estado == 'Programada' or cita.estado == 'Reprogramada':
                cita.estado = 'Atendida'
                cita.save()
                
                LogAuditoria.objects.create(
                    usuario=request.user,
                    accion='ATENDER_CITA',
                    tabla_afectada='Cita',
                    id_registro_afectado=cita.id,
                    detalles='Cita marcada como Atendida.'
                )
                messages.success(request, 'Cita marcada como Atendida.')
            else:
                messages.error(request, 'Solo se pueden atender citas Programadas o Reprogramadas.')
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
                
            if fecha_inicio < now():
                messages.error(request, "No se pueden reagendar citas a fechas u horas pasadas.")
                return redirect('agenda')
                
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
            
            # ENVIAR EMAIL DE REAGENDAMIENTO (ASÍNCRONO)
            if cita.paciente.correo_electronico:
                asunto = "Cita Reagendada - AncaneSoft"
                titulo = "¡Cita Modificada!"
                mensaje_principal = "Tu cita ha sido reprogramada a un nuevo horario."
                fecha_str = fecha_inicio.strftime('%Y-%m-%d a las %I:%M %p')
                enviar_correo_html_async(asunto, titulo, cita.paciente.nombre_completo, mensaje_principal, cita.tipo_cita, fecha_str, cita.paciente.correo_electronico)
                
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

